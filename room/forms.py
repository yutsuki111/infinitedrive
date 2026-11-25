from django import forms
from django.db import models
from django.forms.models import ModelForm
from driveapp.models import Room, RoomParticipation


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_code', 'room_name', 'passphrase_hash']


# class CreateJoinRoomForm(ModelForm):
#     class Meta:
#         model = RoomParticipation

#         fields = ['nickname', 'room']

#         def __init__(self, *args, **kwargs):
#             room = kwargs.pop('room')
#             self.fields['room'].queryset = room.objects.filter(id=id)


# class JoinRoomForm(forms.ModelForm):

#     nickname = forms.CharField(label="出版社", max_length=255, required=False)

#     class Meta:
#         model = Room
#         fields = ['room_code', 'passphrase_hash']

#         # fields = ['nickname', 'room.room_code', 'room.passphrase_hash']
#         # fields = ['nickname', 'participations.room_code', 'participations.passphrase_hash']
#         # fields = ['nickname', 'room_id.room_code', 'room_id.passphrase_hash']
#         # fields = '__all__'


class JoinRoomForm(forms.ModelForm):
    room_code = forms.CharField(max_length=4, label="部屋番号")
    passphrase = forms.CharField(max_length=255, label="合言葉")

    class Meta:
        model = RoomParticipation
        fields = ['nickname']

        # fields = ['nickname', 'room.room_code', 'room.passphrase_hash']
        # fields = ['nickname', 'participations.room_code', 'participations.passphrase_hash']
        # fields = ['nickname', 'room_id.room_code', 'room_id.passphrase_hash']
        # fields = '__all__'
