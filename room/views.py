"""
部屋管理（SCR-06 部屋作成 ／ SCR-07 部屋参加 ／ SCR-09 部屋画面）

・会員もゲストも使える（ゲストは guest_sessions で見分ける。room/utils.py 参照）
・作成・参加したら、session に「今の参加情報」を入れる
  → ほかの画面は room.utils.get_current_participation(request) で取れる
・合言葉はハッシュ化して保存する（Django の make_password / check_password）
・部屋番号は4桁を自動で発行する
"""

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from django.utils.timezone import localtime

from drive.utils import get_active_mission, get_current_drive
from driveapp.models import Room, RoomParticipation, TimelinePost

from .forms import CreateRoomForm, JoinRoomForm
from .utils import (
    clear_current_participation,
    generate_room_code,
    get_current_participation,
    get_or_create_guest,
    set_current_participation,
)


# ------------------------------------------------------------
# SCR-06 部屋作成
# ------------------------------------------------------------
def room_create_view(request):
    # すでにどこかの部屋に入っている人は、その部屋に戻す（二重参加の防止）
    current = get_current_participation(request)
    if current:
        messages.info(request, f'すでに部屋「{current.room.room_name}」に参加中です。')
        return redirect('room:top', room_id=current.room_id)

    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            with transaction.atomic():
                room = Room.objects.create(
                    room_code=generate_room_code(),
                    room_name=data['room_name'],
                    passphrase_hash=make_password(data['passphrase']),
                )
                participation = _join(request, room, data['nickname'], role='leader')
            set_current_participation(request, participation)
            return redirect('room:top', room_id=room.room_id)
    else:
        form = CreateRoomForm(initial={'nickname': _default_nickname(request)})

    return render(request, 'room/room_create.html', {'form': form})


# ------------------------------------------------------------
# SCR-07 部屋参加
# ------------------------------------------------------------
def room_join_view(request):
    current = get_current_participation(request)
    if current:
        messages.info(request, f'すでに部屋「{current.room.room_name}」に参加中です。')
        return redirect('room:top', room_id=current.room_id)

    if request.method == 'POST':
        form = JoinRoomForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            room = (Room.objects.exclude(status='dissolved')
                    .filter(room_code=data['room_code']).first())
            # 部屋がない・合言葉が違う、はどちらも同じメッセージにする（どちらが違うか教えない）
            if room is None or not check_password(data['passphrase'], room.passphrase_hash):
                form.add_error(None, '部屋番号または合言葉が正しくありません。')
            else:
                participation = _join(request, room, data['nickname'], role='member')
                set_current_participation(request, participation)
                return redirect('room:top', room_id=room.room_id)
    else:
        form = JoinRoomForm(initial={'nickname': _default_nickname(request)})

    return render(request, 'room/room_join.html', {'form': form})


# ------------------------------------------------------------
# SCR-09 部屋画面
# ------------------------------------------------------------
def room_view(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    me = get_current_participation(request)
    if me is None or me.room_id != room.room_id:
        messages.error(request, 'この部屋には参加していません。部屋番号と合言葉で参加してください。')
        return redirect('room:join')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'leave':
            return _leave(request, me)
        # ガチャは drive アプリ（drive:gacha）で処理済み
        # TODO(ドライブ担当)：depart / arrive / arrive_all / post / mission も drive アプリに作る
        messages.info(request, 'この機能はまだ作成中です。')
        return redirect('room:top', room_id=room.room_id)

    members = list(room.participations.filter(status='joined').order_by('joined_at'))
    drive = get_current_drive(room)
    last_companion, last_mood = request.session.get('gacha_conditions') or [None, None]
    return render(request, 'room/room.html', {
        'room_id': room.room_id,
        'room': room,
        'status': room.status,               # waiting / gacha_fixed / driving
        'is_leader': me.role == 'leader',
        'is_solo': len(members) == 1,
        'members': [
            {'id': m.pk, 'nickname': m.nickname, 'is_leader': m.role == 'leader'}
            for m in members
        ],
        # ガチャの結果（drive アプリ）
        'destination': drive.destination if drive else None,
        'mission': get_active_mission(drive),
        'companion': drive.companion_tag if drive else last_companion,
        'mood': drive.mood_tag if drive else last_mood,
        'posts': _timeline(room),
    })


# ------------------------------------------------------------
# 退出（一般参加者）・解散（代表者）
# ------------------------------------------------------------
def _leave(request, me):
    room = me.room
    if me.role == 'leader':
        # 解散：部屋を物理削除（参加情報・ドライブ・投稿も一緒に消える。ドライブ履歴は残る）
        name = room.room_name
        room.delete()
        messages.success(request, f'部屋「{name}」を解散しました。')
    else:
        me.status = 'left'
        me.left_at = timezone.now()
        me.save()
        messages.success(request, f'部屋「{room.room_name}」から退出しました。')
    clear_current_participation(request)
    return redirect('driveapp:home')


# ------------------------------------------------------------
# タイムライン（古い順）
# ------------------------------------------------------------
def _timeline(room):
    # 投稿者の名前は、その部屋での参加ニックネームを使う（退出した人も含める）
    names = {}
    for p in room.participations.all():
        names[('a', p.account_id)] = p.nickname
        names[('g', p.guest_id)] = p.nickname
    posts = []
    for post in TimelinePost.objects.filter(room=room).order_by('created_at'):
        if post.account_id:
            nickname = names.get(('a', post.account_id), '')
        elif post.guest_id:
            nickname = names.get(('g', post.guest_id), '')
        else:
            nickname = ''
        image = post.images.order_by('display_order').first()
        posts.append({
            'post_type': post.post_type,
            'nickname': nickname,
            'time': localtime(post.created_at).strftime('%H:%M'),
            'content': post.content or '',
            'image_url': image.image_url if image else None,
        })
    return posts


# ------------------------------------------------------------
# 小さな部品
# ------------------------------------------------------------
def _join(request, room, nickname, role):
    """会員なら account、ゲストなら guest を付けて参加情報を作る"""
    if request.user.is_authenticated:
        return RoomParticipation.objects.create(
            room=room, account=request.user, nickname=nickname, role=role)
    guest = get_or_create_guest(request, nickname)
    return RoomParticipation.objects.create(
        room=room, guest=guest, nickname=nickname, role=role)


def _default_nickname(request):
    """会員は表示名を最初から入れておく（画面設計書：会員は表示名を初期設定）"""
    if request.user.is_authenticated:
        return getattr(request.user, 'display_name', '') or request.user.get_username()
    return ''

