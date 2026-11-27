import re
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
#ドライブ履歴と称号のモデルはdriveappにあるのでインポート
from driveapp.models import DriveHistory, DriveHistoryParticipant, AccountAchievement

# Create your views here.

#SCR-04 プロフィール（ログインした会員だけ）
@method_decorator(login_required, name="dispatch")
class ProfileView(ListView):
    #使用するテンプレート
    template_name = "mypage/profile.html"
    #テンプレートで使う名前
    context_object_name = "histories"

    #自分が参加したドライブ履歴だけを新しい順に取り出す
    def get_queryset(self):
        return DriveHistory.objects.filter(
            participants__account=self.request.user
        ).distinct().order_by("-started_at")

    #称号の一覧と件数もテンプレートに渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titles"] = AccountAchievement.objects.filter(
            account=self.request.user
        ).select_related("achievement").order_by("acquired_at")
        context["drive_count"] = context["histories"].count()
        context["title_count"] = context["titles"].count()
        return context


#SCR-05 ドライブ履歴詳細（自分が参加した履歴だけ）
@method_decorator(login_required, name="dispatch")
class HistoryDetailView(DetailView):
    #対象となるモデル
    model = DriveHistory
    #使用するテンプレート
    template_name = "mypage/history_detail.html"
    #テンプレートで使う名前
    context_object_name = "history"
    #URLの<int:history_id>をIDとして使う
    pk_url_kwarg = "history_id"

    #他の人の履歴を開けないようにする（開こうとすると404）
    def get_queryset(self):
        return super().get_queryset().filter(participants__account=self.request.user).distinct()

    #自分の参加情報（称号・写真）と、ミッションの一覧を渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        participation = DriveHistoryParticipant.objects.filter(
            drive_history=self.object, account=self.request.user
        ).first()
        context["participation"] = participation
        context["titles"] = split_text(participation.result if participation else "")
        context["missions"] = split_text(self.object.mission_title_snapshot)
        return context


#「絶景ハンター、ナイトドライバー」のような文字列をリストにする
#区切りは「、」「,」「，」「改行」のどれでもOK
def split_text(text):
    if not text:
        return []
    return [t.strip() for t in re.split(r"[、,，\n]", text) if t.strip()]
