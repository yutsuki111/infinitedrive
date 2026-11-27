from django.views.generic import FormView, TemplateView
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
#部屋・参加者・タイムラインのモデルはdriveappにあるのでインポート
from driveapp.models import Room, RoomParticipation, TimelinePost
#ガチャの結果はdriveアプリから取り出す
from drive.utils import get_active_mission, get_current_drive
from .forms import CreateRoomForm, JoinRoomForm
from .utils import (
    clear_current_participation,
    generate_room_code,
    get_current_participation,
    get_or_create_guest,
    set_current_participation,
)

# Create your views here.

#SCR-06 部屋作成（会員もゲストも使える）
class RoomCreateView(FormView):
    #使用するフォーム
    form_class = CreateRoomForm
    #使用するテンプレート
    template_name = "room/room_create.html"

    def dispatch(self, request, *args, **kwargs):
        #すでにどこかの部屋に入っている人は、その部屋に戻す（二重参加の防止）
        current = get_current_participation(request)
        if current:
            messages.info(request, f"すでに部屋「{current.room.room_name}」に参加中です。")
            return redirect("room:top", room_id=current.room_id)
        return super().dispatch(request, *args, **kwargs)

    #会員はニックネームに表示名を最初から入れておく
    def get_initial(self):
        return {"nickname": default_nickname(self.request)}

    def form_valid(self, form):
        data = form.cleaned_data
        #部屋と参加情報は、両方作れたときだけ保存する
        with transaction.atomic():
            room = Room.objects.create(
                room_code=generate_room_code(),
                room_name=data["room_name"],
                #合言葉はハッシュ化して保存する
                passphrase_hash=make_password(data["passphrase"]),
            )
            participation = join_room(self.request, room, data["nickname"], "leader")
        set_current_participation(self.request, participation)
        return redirect("room:top", room_id=room.room_id)


#SCR-07 部屋参加（会員もゲストも使える）
class RoomJoinView(FormView):
    #使用するフォーム
    form_class = JoinRoomForm
    #使用するテンプレート
    template_name = "room/room_join.html"

    def dispatch(self, request, *args, **kwargs):
        #すでにどこかの部屋に入っている人は、その部屋に戻す
        current = get_current_participation(request)
        if current:
            messages.info(request, f"すでに部屋「{current.room.room_name}」に参加中です。")
            return redirect("room:top", room_id=current.room_id)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {"nickname": default_nickname(self.request)}

    def form_valid(self, form):
        data = form.cleaned_data
        room = Room.objects.exclude(status="dissolved").filter(room_code=data["room_code"]).first()
        #部屋がない・合言葉が違う、はどちらも同じメッセージにする（どちらが違うか教えない）
        if room is None or not check_password(data["passphrase"], room.passphrase_hash):
            form.add_error(None, "部屋番号または合言葉が正しくありません。")
            return self.form_invalid(form)
        participation = join_room(self.request, room, data["nickname"], "member")
        set_current_participation(self.request, participation)
        return redirect("room:top", room_id=room.room_id)


#SCR-09 部屋画面（参加している人だけ）
class RoomView(TemplateView):
    #使用するテンプレート
    template_name = "room/room.html"

    def dispatch(self, request, *args, **kwargs):
        self.room = Room.objects.filter(pk=kwargs["room_id"]).first()
        #解散された部屋（もうない部屋）を開いたときは、404ではなくホームに戻す
        if self.room is None:
            clear_current_participation(request)
            messages.info(request, "この部屋はすでに解散されています。")
            return redirect("driveapp:home")
        self.me = get_current_participation(request)
        #この部屋に参加していない人は、参加画面へ
        if self.me is None or self.me.room_id != self.room.room_id:
            messages.error(request, "この部屋には参加していません。部屋番号と合言葉で参加してください。")
            return redirect("room:join")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.room
        members = room.participations.filter(status="joined").order_by("joined_at")
        drive = get_current_drive(room)
        #ガチャ前は、前回選んだ条件を表示する
        last_companion, last_mood = self.request.session.get("gacha_conditions") or [None, None]
        context["room"] = room
        context["room_id"] = room.room_id
        #waiting（待機中）／gacha_fixed（ガチャ確定後）／driving（走行中）
        context["status"] = room.status
        context["is_leader"] = self.me.role == "leader"
        context["is_solo"] = members.count() == 1
        context["members"] = [
            {"id": m.pk, "nickname": m.nickname, "is_leader": m.role == "leader"}
            for m in members
        ]
        #ガチャの結果
        context["destination"] = drive.destination if drive else None
        context["mission"] = get_active_mission(drive)
        context["companion"] = drive.companion_tag if drive else last_companion
        context["mood"] = drive.mood_tag if drive else last_mood
        context["posts"] = make_timeline(room)
        return context

    #ボタンはhiddenのactionで見分ける
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "leave":
            return leave_room(request, self.me)
        #ガチャはdriveアプリ（drive:gacha）で処理する
        #出発・到着・投稿・ミッション報告はこれから作る
        messages.info(request, "この機能はまだ作成中です。")
        return redirect("room:top", room_id=self.room.room_id)


#退出（一般参加者）・解散（代表者）
def leave_room(request, me):
    room = me.room
    if me.role == "leader":
        #解散：部屋を削除する（参加情報・ドライブ・投稿も一緒に消える。ドライブ履歴は残る）
        name = room.room_name
        room.delete()
        messages.success(request, f"部屋「{name}」を解散しました。")
    else:
        me.status = "left"
        me.left_at = timezone.now()
        me.save()
        messages.success(request, f"部屋「{room.room_name}」から退出しました。")
    clear_current_participation(request)
    return redirect("driveapp:home")


#タイムラインの投稿を古い順にリストにする
def make_timeline(room):
    #投稿者の名前は、その部屋での参加ニックネームを使う（退出した人も含める）
    names = {}
    for p in room.participations.all():
        names[("a", p.account_id)] = p.nickname
        names[("g", p.guest_id)] = p.nickname
    posts = []
    for post in TimelinePost.objects.filter(room=room).order_by("created_at"):
        if post.account_id:
            nickname = names.get(("a", post.account_id), "")
        elif post.guest_id:
            nickname = names.get(("g", post.guest_id), "")
        else:
            nickname = ""
        image = post.images.order_by("display_order").first()
        posts.append({
            "post_type": post.post_type,
            "nickname": nickname,
            "time": timezone.localtime(post.created_at).strftime("%H:%M"),
            "content": post.content or "",
            "image_url": image.image_url if image else None,
        })
    return posts


#会員ならaccount、ゲストならguestを付けて参加情報を作る
def join_room(request, room, nickname, role):
    if request.user.is_authenticated:
        return RoomParticipation.objects.create(
            room=room, account=request.user, nickname=nickname, role=role)
    guest = get_or_create_guest(request, nickname)
    return RoomParticipation.objects.create(
        room=room, guest=guest, nickname=nickname, role=role)


#会員は表示名、ゲストは空にする
def default_nickname(request):
    if request.user.is_authenticated:
        return getattr(request.user, "display_name", "") or request.user.get_username()
    return ""
