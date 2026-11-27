#部屋まわりの共通処理
#「今どの部屋にいて、自分は誰か」は、次の1行で取れる
#  from room.utils import get_current_participation
#  p = get_current_participation(request)   #部屋に入っていなければ None
#  p.room / p.role / p.nickname / p.account / p.guest
#会員もゲストも同じ書き方で使える
import hashlib
import random
import secrets
from datetime import timedelta

from django.utils import timezone

from driveapp.models import GuestSession, Room, RoomParticipation

#session に保存するキーの名前
SESSION_PARTICIPATION = "participation_id"
SESSION_GUEST_TOKEN = "guest_token"

#ゲストの有効期限
GUEST_LIFETIME = timedelta(hours=24)


#今参加している部屋（RoomParticipation）を返す。なければ None
def get_current_participation(request):
    active = RoomParticipation.objects.select_related("room").filter(
        status="joined",
    ).exclude(room__status="dissolved")

    #1. session に入っている参加情報が、本当に自分のものか確かめて返す
    pid = request.session.get(SESSION_PARTICIPATION)
    if pid:
        p = active.filter(pk=pid).first()
        if p and _is_mine(request, p):
            return p
        request.session.pop(SESSION_PARTICIPATION, None)

    #2. 会員なら、ログインし直した後でも自分の参加情報を探せる
    if request.user.is_authenticated:
        p = active.filter(account=request.user).order_by("-joined_at").first()
        if p:
            request.session[SESSION_PARTICIPATION] = p.pk
            return p

    return None


def set_current_participation(request, participation):
    request.session[SESSION_PARTICIPATION] = participation.pk


def clear_current_participation(request):
    request.session.pop(SESSION_PARTICIPATION, None)


def _is_mine(request, p):
    if request.user.is_authenticated:
        return p.account_id == request.user.pk
    guest = get_guest(request)
    return guest is not None and p.guest_id == guest.pk


#ゲスト（ログインしていない人）
#ブラウザの session にランダムな合言葉（トークン）を入れ、
#データベースにはそのハッシュだけを保存する（guest_sessions）。
def get_guest(request):
    token = request.session.get(SESSION_GUEST_TOKEN)
    if not token:
        return None
    return GuestSession.objects.filter(
        session_token_hash=_hash(token),
        status="active",
        expires_at__gt=timezone.now(),
    ).first()


def get_or_create_guest(request, nickname):
    guest = get_guest(request)
    if guest:
        guest.display_name = nickname
        guest.expires_at = timezone.now() + GUEST_LIFETIME
        guest.save()
        return guest

    token = secrets.token_urlsafe(32)
    guest = GuestSession.objects.create(
        session_token_hash=_hash(token),
        display_name=nickname,
        expires_at=timezone.now() + GUEST_LIFETIME,
    )
    request.session[SESSION_GUEST_TOKEN] = token
    return guest


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


#部屋番号（4桁の数字）を、使われていないものから発行する
def generate_room_code():
    used = set(Room.objects.values_list("room_code", flat=True))
    free = [f"{n:04d}" for n in range(10000) if f"{n:04d}" not in used]
    if not free:
        raise RuntimeError("部屋番号の空きがありません。")
    return random.choice(free)
