from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from driveapp.models import Room, RoomParticipation


# Create your views here.
class RoomView(TemplateView):
    template_name = "room/room.html"


class RoomCreateView(CreateView):
    template_name = "room/room_create.html"
    form_class = CreateRoomForm

    def form_valid(self, form):
        
        # 登録する前に、上で確認作業はしないといけない
        response = super().form_valid(form)
        # 登録が完了してから下が動作

        room_code = form.cleaned_data.get('room_code')
        room = Room.objects.get(room_code=room_code)
        print(room)
        print(room.room_id)
        # 会員の場合
        if not self.request.user.id is None:
            RoomParticipation.objects.create(room_id=room.room_id, account_id=self.request.user.id, nickname=self.request.user.display_name, role="leader", safety_agreed=False, drive_status="ready", status="joined")
        # ゲストの場合
        else:
            pass

        return response

    def get_success_url(self):
        return reverse('room:top', kwargs={'room_id':self.object.room_id})


class RoomJoinView(LoginRequiredMixin, CreateView):
    template_name = "room/room_join.html"
    form_class = JoinRoomForm

    def form_valid(self, form):
        user = self.object

        # formの値を取得
        model = form.save(commit=False)

        # try:
        #     user = User.objects.get(pk=id)
        #     # ここに何か書く
        # except User.DoesNotExist:
        #     pass
        # 部屋の存在と合言葉を確認する
        room_exists = Room.objects.get(room_code=model.room_code, passphrase_hash=model.passphrase_hash)

        # 会員IDまたはゲストIDを取得する
        USER_ID = self.request.user.id

        # 現在の参加人数と参加状況を確認する
        CurrentNumberOfParticipants = RoomParticipation.objects.all.filter(left_at__isnull=True).count()

        MAX_PARTICIPANTS_NUMBER = 20

        # 最大を超えていた場合、エラーとしたい
        if (CurrentNumberOfParticipants > MAX_PARTICIPANTS_NUMBER):
            pass

        # 会員の場合
        if not self.request.user.id is None:
            ParticipationStatus = RoomParticipation.objects.all.filter(account_id=self.request.user.id, status="参加中").count()
        # ゲストの場合
        else:
            pass

        # 別の部屋に参加していた場合、エラーとしたい
        if not ParticipationStatus == 0:
            pass

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('room:top', kwargs={'room_id':self.object.room_id})
