from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from driveapp.models import Destination, Mission
from .forms import DestinationForm, MissionForm


#マスタ管理画面（SCR-14）
#ログインしていない場合はログイン画面へ
@method_decorator(login_required, name="dispatch")
class ManageView(TemplateView):
    template_name = "master/manage.html"

    def dispatch(self, request, *args, **kwargs):
        #管理者（is_staff）じゃない場合はホームに戻す
        if not request.user.is_staff:
            messages.error(request, "マスタ管理は管理者のみ利用できます。")
            return redirect("driveapp:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #削除されていないもの（status="active"）だけ新しい順に表示
        context["destinations"] = Destination.objects.filter(status="active").order_by("-updated_at")
        context["missions"] = Mission.objects.filter(status="active").order_by("-updated_at")
        #最初に開くタブ（目的地 or ミッション）
        context["active_tab"] = kwargs.get("active_tab") or self.request.GET.get("tab", "destination")
        return context

    #保存ボタン・削除ボタンが押されたとき
    def post(self, request, *args, **kwargs):
        master_type = request.POST.get("master_type")
        action = request.POST.get("action")

        #目的地かミッションかで、使うモデルとフォームを切り替える
        if master_type == "destination":
            model = Destination
            form_class = DestinationForm
        elif master_type == "mission":
            model = Mission
            form_class = MissionForm
        else:
            messages.error(request, "不正な操作です。")
            return redirect("master:manage")

        #編集・削除のときは対象のデータを取得（新規追加のときは空）
        target = None
        master_id = request.POST.get("master_id")
        if master_id:
            target = get_object_or_404(model, pk=master_id, status="active")

        #保存（追加・編集）
        if action == "save":
            #instanceを渡すと編集、渡さないと新規追加になる
            form = form_class(request.POST, instance=target)
            if form.is_valid():
                form.save()
                messages.success(request, f"「{form.instance}」を保存しました。")
            else:
                #エラーのときは入力した内容を残してフォームを開いたまま表示
                context = self.get_context_data(active_tab=master_type)
                context["error"] = list(form.errors.values())[0][0]
                context["form_data"] = {
                    "type": master_type,
                    "id": master_id or "",
                    "name": request.POST.get("name") or request.POST.get("title", ""),
                    "lat": request.POST.get("latitude", ""),
                    "lng": request.POST.get("longitude", ""),
                    "companion": request.POST.get("companion_tag", ""),
                    "mood": request.POST.get("mood_tag", ""),
                }
                return self.render_to_response(context)

        #削除
        elif action == "delete" and target:
            #過去のドライブで使われているものは消さずに非表示（status="deleted"）にする
            if master_type == "destination":
                used = target.drives.exists()
            else:
                used = target.drive_missions.exists()
            if used:
                target.status = "deleted"
                target.save()
                messages.success(request, f"「{target}」は過去のドライブで使われているため、非表示にしました。")
            else:
                target.delete()
                messages.success(request, f"「{target}」を削除しました。")

        #処理が終わったら一覧に戻る（さっき操作したタブを開く）
        return redirect(reverse("master:manage") + f"?tab={master_type}")
