"""
部屋作成（SCR-06）・部屋参加（SCR-07）の入力チェック

画面設計書のバリデーション：
  部屋名       … 必須／最大50文字
  合言葉       … 必須／最大20文字／半角英数字
  ニックネーム … 必須／最大20文字
  部屋番号     … 必須／数字4桁（参加のときだけ。作成のときは自動で発行する）
"""

from django import forms
from django.core.validators import RegexValidator

passphrase_validator = RegexValidator(r'^[A-Za-z0-9]+$', '合言葉は半角英数字で入力してください。')
room_code_validator = RegexValidator(r'^[0-9]{4}$', '部屋番号は4桁の数字で入力してください。')

REQUIRED = {'required': '入力してください。'}


class CreateRoomForm(forms.Form):
    room_name = forms.CharField(label='部屋名', max_length=50, error_messages=REQUIRED)
    passphrase = forms.CharField(label='合言葉', max_length=20,
                                 validators=[passphrase_validator], error_messages=REQUIRED)
    nickname = forms.CharField(label='参加ニックネーム', max_length=20, error_messages=REQUIRED)


class JoinRoomForm(forms.Form):
    room_code = forms.CharField(label='部屋番号', max_length=4,
                                validators=[room_code_validator], error_messages=REQUIRED)
    passphrase = forms.CharField(label='合言葉', max_length=20,
                                 validators=[passphrase_validator], error_messages=REQUIRED)
    nickname = forms.CharField(label='参加ニックネーム', max_length=20, error_messages=REQUIRED)
