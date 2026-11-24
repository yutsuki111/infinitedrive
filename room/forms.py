from django import forms
from driveapp.models import Room


class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_code', 'room_name', 'passphrase_hash']


class JoinRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_code', 'passphrase_hash']
