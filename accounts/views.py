from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from .forms import CreateUserForm
from django.urls import reverse_lazy


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
