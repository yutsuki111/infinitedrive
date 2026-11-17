from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CreateUserForm
from .models import CustomUser


class RegisterView(CreateView):
    form_class = CreateUserForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy('accounts:register_success')

    def form_valid(self, form):
        # フォームオブジェクトの値をデータベースへ保存
        user = form.save()
        self.object = user
        # 戻り値はスーパークラスのform_valid()の戻り値(HttpResponseRedirect)
        return super().form_valid(form)


class RegisterSuccessView(TemplateView):
    template_name = "accounts/kari_register_success.html"

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_queryset(self):
        return CustomUser.objects.get(id=self.request.user.id)