from django.shortcuts import redirect, render

# ============================================================
# 【今の段階】画面を表示するための仮の views です。
#   - フロント担当：HTML は driveapp/templates/driveapp/ の中を編集してOK
#   - データは全部 DUMMY_ で始まる仮データ。後で DB に差し替える
#   - バックエンド担当：TODO の場所に認証・DB処理を入れる
# ============================================================

# ---- 仮データ（画面確認用）----
DUMMY_USER = {'nickname': 'ドライバー太郎'}
DUMMY_TITLES = ['はじめてのドライブ', 'ご当地グルメ好き']
DUMMY_HISTORIES = [
    {'id': 1, 'date': '2026/11/01', 'destination': '道の駅 ○○'},
    {'id': 2, 'date': '2026/11/08', 'destination': '海沿いの展望台'},
]
DUMMY_HISTORY = {
    'date': '2026/11/01',
    'destination': '道の駅 ○○',
    'titles': ['はじめてのドライブ'],
    'photo_url': None,
}
DUMMY_DESTINATIONS = [
    {'name': '道の駅 ○○', 'rating': 4},
    {'name': '海沿いの展望台', 'rating': 5},
]
DUMMY_MISSIONS = [
    {'name': '地元の野菜を買う'},
    {'name': 'ご当地ソフトを食べる'},
]
DUMMY_SHARE_TEXT = '今日は道の駅 ○○ に行ってきました！ 星4つ！'


# ---- SCR-01 ログイン ----
def login_view(request):
    if request.method == 'POST':
        # TODO(バックエンド)：user_id / password で認証する
        return redirect('driveapp:home')
    return render(request, 'driveapp/login.html')


# ---- SCR-02 アカウント登録 ----
def register_view(request):
    if request.method == 'POST':
        # TODO(バックエンド)：アカウントを保存する
        return redirect('driveapp:home')
    return render(request, 'driveapp/register.html')


# ---- SCR-03 ホーム ----
def home_view(request):
    return render(request, 'driveapp/home.html', {'user': DUMMY_USER})


# ---- SCR-04 プロフィール ----
def profile_view(request):
    return render(request, 'driveapp/profile.html', {
        'user': DUMMY_USER,
        'titles': DUMMY_TITLES,
        'histories': DUMMY_HISTORIES,
    })


# ---- SCR-05 ドライブ履歴詳細 ----
def history_detail_view(request):
    # TODO(バックエンド)：どのドライブかを ID で受け取る（設計に合わせて urls.py も変更）
    return render(request, 'driveapp/history_detail.html', {'history': DUMMY_HISTORY})


# ---- SCR-06 部屋作成 ----
def room_create_view(request):
    if request.method == 'POST':
        # TODO(バックエンド)：部屋を作成する
        return redirect('driveapp:room')
    return render(request, 'driveapp/room_create.html')


# ---- SCR-07 部屋参加 ----
def room_join_view(request):
    if request.method == 'POST':
        # TODO(バックエンド)：部屋番号と合言葉を照合する
        return redirect('driveapp:role_select')
    return render(request, 'driveapp/room_join.html')


# ---- SCR-08 役割選択 ----
def role_select_view(request):
    if request.method == 'POST':
        # TODO(バックエンド)：役割と安全同意を保存する
        return redirect('driveapp:room')
    return render(request, 'driveapp/role_select.html')


# ---- SCR-09 部屋画面（メイン）----
def room_view(request):
    return render(request, 'driveapp/room.html', {'destinations': DUMMY_DESTINATIONS})


# ---- SCR-10 目的地評価 ----
def evaluation_view(request):
    if request.method == 'POST':
        # TODO(バックエンド)：星の評価を保存する
        return redirect('driveapp:result')
    return render(request, 'driveapp/evaluation.html')


# ---- SCR-11 リザルト ----
def result_view(request):
    return render(request, 'driveapp/result.html', {'titles': DUMMY_TITLES})


# ---- SCR-12 割り勘電卓 ----
def calculator_view(request):
    # TODO(バックエンド)：距離・人数・燃費・単価から計算する
    return render(request, 'driveapp/calculator.html')


# ---- SCR-13 ドライブ結果共有 ----
def share_view(request):
    return render(request, 'driveapp/share.html', {'share_text': DUMMY_SHARE_TEXT})


# ---- SCR-14 マスタ管理 ----
def master_manage_view(request):
    return render(request, 'driveapp/master_manage.html', {
        'destinations': DUMMY_DESTINATIONS,
        'missions': DUMMY_MISSIONS,
    })
