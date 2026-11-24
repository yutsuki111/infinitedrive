"""
SCR-14 マスタ管理（目的地・ミッションの追加・編集・削除）

・データ（Destination / Mission）は driveapp/models.py にあるものを使う
  （models は driveapp にまとめておく、というチームの方針）

・管理者（is_staff が True のユーザー）だけが使える
・画面から送られてくる値（master/manage.html のフォーム）
    保存：action=save, master_type（destination / mission）, master_id（新規は空）,
          master_name, latitude, longitude, companion_tag, mood_tag
    削除：action=delete, master_type, master_id
・削除のルール（画面設計書・UC「削除する」）
    過去のドライブから使われているデータ → 非表示にする（status を 'deleted'）
    まだ一度も使われていないデータ     → 完全に削除する
"""

from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.shortcuts import redirect, render

from driveapp.models import Destination, Mission

# 画面の選択肢（master/manage.html の <select> と同じもの）
COMPANION_TAGS = ['1人', '友達', '恋人', '家族']
MOOD_TAGS = ['エモい', '夜景・絶景', 'のんびり']


def manage_view(request):
    # ---- 管理者以外は入れない ----
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if not request.user.is_staff:
        messages.error(request, 'マスタ管理は管理者のみ利用できます。')
        return redirect('driveapp:home')

    if request.method == 'POST':
        action = request.POST.get('action')
        master_type = request.POST.get('master_type')
        if master_type not in ('destination', 'mission'):
            messages.error(request, '不正な操作です。')
            return redirect('master:manage')

        if action == 'save':
            error = _save(request, master_type)
            if error:
                # エラーのときは入力内容を残したまま、フォームを開いた状態で表示し直す
                return _render(request, master_type, error=error, form_data={
                    'type': master_type,
                    'id': request.POST.get('master_id', ''),
                    'name': request.POST.get('master_name', ''),
                    'lat': request.POST.get('latitude', ''),
                    'lng': request.POST.get('longitude', ''),
                    'companion': request.POST.get('companion_tag', ''),
                    'mood': request.POST.get('mood_tag', ''),
                })
        elif action == 'delete':
            _delete(request, master_type)
        else:
            messages.error(request, '不正な操作です。')

        # 処理が終わったら一覧に戻る（更新ボタンで二重送信しないように redirect する）
        return redirect(f"{request.path}?tab={master_type}")

    return _render(request, request.GET.get('tab', 'destination'))


# ------------------------------------------------------------
# 一覧画面を表示する
# ------------------------------------------------------------
def _render(request, active_tab, error=None, form_data=None):
    # messages（保存しました、など）を取り出して画面用の message / error に分ける
    message = None
    for m in messages.get_messages(request):
        if m.level_tag == 'error':
            error = error or m.message
        else:
            message = m.message

    return render(request, 'master/manage.html', {
        'destinations': Destination.objects.filter(status='active').order_by('-updated_at'),
        'missions': Mission.objects.filter(status='active').order_by('-updated_at'),
        'active_tab': active_tab if active_tab in ('destination', 'mission') else 'destination',
        'message': message,
        'error': error,
        'form_data': form_data,
    })


# ------------------------------------------------------------
# 追加・更新（エラーがあればメッセージを返す。成功なら None）
# ------------------------------------------------------------
def _save(request, master_type):
    post = request.POST
    master_id = post.get('master_id', '').strip()
    name = post.get('master_name', '').strip()
    companion = post.get('companion_tag', '')
    mood = post.get('mood_tag', '')

    # ---- 入力チェック ----
    if not name:
        return '名称・内容を入力してください。'
    if len(name) > 100:
        return '名称・内容は100文字以内で入力してください。'
    if companion not in COMPANION_TAGS or mood not in MOOD_TAGS:
        return '同行者・気分のタグを選択してください。'

    if master_type == 'destination':
        lat = _to_decimal(post.get('latitude'))
        lng = _to_decimal(post.get('longitude'))
        if lat is None or not (-90 <= lat <= 90):
            return '緯度は -90〜90 の数値で入力してください。'
        if lng is None or not (-180 <= lng <= 180):
            return '経度は -180〜180 の数値で入力してください。'

    # ---- 新規か更新か ----
    model = Destination if master_type == 'destination' else Mission
    if master_id:
        obj = model.objects.filter(pk=master_id, status='active').first() if master_id.isdigit() else None
        if obj is None:
            return '編集するデータが見つかりませんでした。'
    else:
        obj = model()

    # ---- 値を入れて保存 ----
    if master_type == 'destination':
        obj.name = name
        obj.latitude = lat
        obj.longitude = lng
    else:
        obj.title = name
    obj.companion_tag = companion
    obj.mood_tag = mood
    obj.save()

    messages.success(request, f'「{name}」を{"更新" if master_id else "追加"}しました。')
    return None


# ------------------------------------------------------------
# 削除（使われていたら非表示、使われていなければ完全削除）
# ------------------------------------------------------------
def _delete(request, master_type):
    master_id = request.POST.get('master_id', '')
    model = Destination if master_type == 'destination' else Mission
    obj = model.objects.filter(pk=master_id, status='active').first() if master_id.isdigit() else None
    if obj is None:
        messages.error(request, '削除するデータが見つかりませんでした。')
        return

    label = obj.name if master_type == 'destination' else obj.title
    # 目的地はドライブ（drives）から、ミッションはドライブミッション（drive_missions）から使われる
    used = obj.drives.exists() if master_type == 'destination' else obj.drive_missions.exists()

    if used:
        obj.status = 'deleted'
        obj.save()
        messages.success(request, f'「{label}」は過去のドライブで使われているため、非表示にしました。')
    else:
        obj.delete()
        messages.success(request, f'「{label}」を削除しました。')


def _to_decimal(value):
    """文字列を小数点以下6桁の Decimal にする。数値でなければ None"""
    try:
        return Decimal(str(value).strip()).quantize(Decimal('0.000001'))
    except (InvalidOperation, ValueError, TypeError):
        return None
