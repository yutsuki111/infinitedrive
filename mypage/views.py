"""
SCR-04 プロフィール ／ SCR-05 ドライブ履歴詳細

・ログインしている会員だけが使える（ゲストはログイン画面へ）
・データは driveapp/models.py のものを使う
    ドライブ回数   … DriveHistoryParticipant（自分が参加したドライブ履歴）の件数
    獲得称号       … AccountAchievement（自分が獲得した称号）
    ドライブ履歴   … DriveHistoryParticipant → DriveHistory
・履歴詳細は「自分が参加したドライブ」だけ見られる（他人の履歴のIDを打っても 404）
"""

import re

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from driveapp.models import AccountAchievement, DriveHistoryParticipant


# ------------------------------------------------------------
# SCR-04 プロフィール
# ------------------------------------------------------------
@login_required
def profile_view(request):
    user = request.user

    # 獲得称号（古い順）
    titles = [
        aa.achievement.name
        for aa in AccountAchievement.objects
        .filter(account=user)
        .select_related('achievement')
        .order_by('acquired_at')
    ]

    # ドライブ履歴（新しい順）
    participations = (
        DriveHistoryParticipant.objects
        .filter(account=user)
        .select_related('drive_history')
        .order_by('-drive_history__started_at')
    )
    histories = [
        {
            'id': p.drive_history.pk,
            'date': _fmt(p.drive_history.started_at, '%Y/%m/%d'),
            'destination': p.drive_history.destination_name_snapshot,
        }
        for p in participations
    ]

    return render(request, 'mypage/profile.html', {
        'titles': titles,
        'histories': histories,
        'drive_count': len(histories),
        'title_count': len(titles),
    })


# ------------------------------------------------------------
# SCR-05 ドライブ履歴詳細
# ------------------------------------------------------------
@login_required
def history_detail_view(request, history_id):
    participation = (
        DriveHistoryParticipant.objects
        .filter(account=request.user, drive_history_id=history_id)
        .select_related('drive_history')
        .first()
    )
    if participation is None:
        # 存在しない履歴、または自分が参加していない履歴
        raise Http404('ドライブ履歴が見つかりません。')

    h = participation.drive_history
    return render(request, 'mypage/history_detail.html', {
        'history': {
            'destination': h.destination_name_snapshot,
            'started_at': _fmt(h.started_at, '%Y/%m/%d %H:%M'),
            'ended_at': _fmt(h.ended_at, '%Y/%m/%d %H:%M'),
            # 獲得称号・達成ミッションは文字列で保存されているので、区切って一覧にする
            'titles': _split(participation.result),
            'missions': _split(h.mission_title_snapshot),
            'photo_url': participation.saved_image_url,
        },
    })


def _fmt(dt, pattern):
    """日時を日本時間の文字列にする（None なら空文字）"""
    if dt is None:
        return ''
    return timezone.localtime(dt).strftime(pattern)


def _split(text):
    """「絶景ハンター、ナイトドライバー」のような文字列をリストにする。
    区切りは「、」「,」「，」「改行」のどれでもOK"""
    if not text:
        return []
    return [t.strip() for t in re.split(r'[、,，\n]', text) if t.strip()]
