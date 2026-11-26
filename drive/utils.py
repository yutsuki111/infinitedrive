"""
ドライブまわりの共通処理

    from drive.utils import get_current_drive, get_active_mission

    drive = get_current_drive(room)          # 終わっていない今のドライブ（なければ None）
    mission = get_active_mission(drive)      # 今有効な道草ミッション（Mission）。なければ None
"""

from driveapp.models import Drive

# ガチャの条件（画面設計書・マスタ管理と同じもの）
COMPANION_TAGS = ['1人', '友達', '恋人', '家族']
MOOD_TAGS = ['エモい', '夜景・絶景', 'のんびり']


def get_current_drive(room):
    """部屋の、まだ終わっていない（finished でない）ドライブを返す"""
    return (Drive.objects.filter(room=room)
            .exclude(status='finished')
            .select_related('destination')
            .order_by('-created_at')
            .first())


def get_active_mission(drive):
    """ドライブに今割り当てられている（引き直しで取り消されていない）ミッション"""
    if drive is None:
        return None
    dm = (drive.drive_missions.filter(status='active')
          .select_related('mission').order_by('-assigned_at').first())
    return dm.mission if dm else None
