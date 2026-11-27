from django import forms
from django.core.validators import RegexValidator

#入力チェック（画面設計書のバリデーション）
#合言葉は半角英数字だけ
passphrase_validator = RegexValidator(r"^[A-Za-z0-9]+$", "合言葉は半角英数字で入力してください。")
#部屋番号は数字4桁
room_code_validator = RegexValidator(r"^[0-9]{4}$", "部屋番号は4桁の数字で入力してください。")
#空のときのメッセージ
REQUIRED = {"required": "入力してください。"}


#SCR-06 部屋作成のフォーム（部屋番号は自動で発行するので入力しない）
class CreateRoomForm(forms.Form):
    room_name = forms.CharField(label="部屋名", max_length=50, error_messages=REQUIRED)
    passphrase = forms.CharField(label="合言葉", max_length=20,
                                 validators=[passphrase_validator], error_messages=REQUIRED)
    nickname = forms.CharField(label="参加ニックネーム", max_length=20, error_messages=REQUIRED)


#SCR-07 部屋参加のフォーム
class JoinRoomForm(forms.Form):
    room_code = forms.CharField(label="部屋番号", max_length=4,
                                validators=[room_code_validator], error_messages=REQUIRED)
    passphrase = forms.CharField(label="合言葉", max_length=20,
                                 validators=[passphrase_validator], error_messages=REQUIRED)
    nickname = forms.CharField(label="参加ニックネーム", max_length=20, error_messages=REQUIRED)
