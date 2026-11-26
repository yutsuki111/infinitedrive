"""
ドライブ準備：ガチャ（UC「ガチャをする」「ガチャを引き直す」）

・代表者だけが引ける（一般参加者が送ってきたらエラー）
・同行者と気分のタグが両方一致する目的地・ミッションから、ランダムに1つずつ選ぶ
・1回目：ドライブ（drives）を作り、ミッションを割り当てる
  引き直し：同じドライブの目的地を差し替え、前のミッションは canceled にして新しく割り当てる
・部屋の状態を gacha_fixed（ガチャ確定後）にして、タイムラインに通知を出す
・走行中（driving）は引けない
"""

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from driveapp.models import Destination, Drive, DriveMission, Mission, TimelinePost
from room.utils import get_current_participation

from .utils import COMPANION_TAGS, MOOD_TAGS, get_active_mission, get_current_drive


@require_POST
def gacha_view(request):
    me = get_current_participation(request)
    if me is None:
        messages.error(request, '部屋に参加していません。')
        return redirect('driveapp:home')

    room = me.room
    back = redirect('room:top', room_id=room.room_id)

    if me.role != 'leader':
        messages.error(request, 'ガチャは代表者だけが引けます。')
        return back
    if room.status == 'driving':
        messages.error(request, '走行中はガチャを引けません。')
        return back

    drive = get_current_drive(room)

    # 条件：画面で選んだもの。「もう一度引く」は条件を送らないので、今のドライブの条件を使う
    companion = request.POST.get('companion') or (drive.companion_tag if drive else None)
    mood = request.POST.get('mood') or (drive.mood_tag if drive else None)
    if companion not in COMPANION_TAGS or mood not in MOOD_TAGS:
        messages.error(request, '同行者と気分を選んでください。')
        return back

    # ---- 抽選 ----
    destinations = Destination.objects.filter(status='active', companion_tag=companion, mood_tag=mood)
    missions = Mission.objects.filter(status='active', companion_tag=companion, mood_tag=mood)

    # 引き直しのときは、できれば前と違うものを出す（候補が1つしかなければ同じでもOK）
    if drive and drive.destination_id and destinations.count() > 1:
        destinations = destinations.exclude(pk=drive.destination_id)
    old_mission = get_active_mission(drive)
    if old_mission and missions.count() > 1:
        missions = missions.exclude(pk=old_mission.pk)

    # 選んだ条件を覚えておく（「該当なし」で戻ったときも、画面の選択がそのまま残るように）
    request.session['gacha_conditions'] = [companion, mood]

    destination = destinations.order_by('?').first()
    mission = missions.order_by('?').first()
    if destination is None or mission is None:
        what = '目的地' if destination is None else 'ミッション'
        messages.error(request, f'「{companion}・{mood}」に合う{what}がまだ登録されていません。条件を変えてください。')
        return back

    # ---- 保存 ----
    with transaction.atomic():
        is_retry = drive is not None and drive.destination_id is not None
        if drive is None:
            drive = Drive(room=room)
        drive.destination = destination
        drive.companion_tag = companion
        drive.mood_tag = mood
        drive.status = 'waiting'
        drive.save()

        drive.drive_missions.filter(status='active').update(status='canceled')
        DriveMission.objects.create(drive=drive, mission=mission)

        room.status = 'gacha_fixed'
        room.save()

        TimelinePost.objects.create(
            drive=drive,
            room=room,
            post_type='system',
            content=(f'{"ガチャを引き直して" if is_retry else "ガチャで"}'
                     f'「{destination.name}」に決まりました！\n道草ミッション：{mission.title}'),
        )

    return back
