from django import forms
from django.forms import ModelForm
from decimal import Decimal
#目的地とミッションのモデルはdriveappにあるのでインポート
from driveapp.models import Destination, Mission

#ガチャの条件（画面のselectと同じもの）
COMPANION_TAGS = ["1人", "友達", "恋人", "家族"]
MOOD_TAGS = ["エモい", "夜景・絶景", "のんびり"]


class DestinationForm(ModelForm):
    #Googleマップの緯度経度は桁が多いので、ここで受け取ってから6桁にそろえる
    latitude = forms.DecimalField(label="緯度")
    longitude = forms.DecimalField(label="経度")

    class Meta:
        #使用するモデル
        model = Destination
        #フォームで使用するフィールド
        fields = ["name", "latitude", "longitude", "companion_tag", "mood_tag"]

    #緯度のチェック（-90〜90）
    def clean_latitude(self):
        latitude = self.cleaned_data["latitude"]
        if latitude < -90 or latitude > 90:
            raise forms.ValidationError("緯度は -90〜90 の数値で入力してください。")
        return latitude.quantize(Decimal("0.000001"))

    #経度のチェック（-180〜180）
    def clean_longitude(self):
        longitude = self.cleaned_data["longitude"]
        if longitude < -180 or longitude > 180:
            raise forms.ValidationError("経度は -180〜180 の数値で入力してください。")
        return longitude.quantize(Decimal("0.000001"))

    #タグが選択肢の中にあるかチェック
    def clean(self):
        cleaned_data = super().clean()
        check_tags(self, cleaned_data)
        return cleaned_data


class MissionForm(ModelForm):
    class Meta:
        model = Mission
        fields = ["title", "companion_tag", "mood_tag"]

    def clean(self):
        cleaned_data = super().clean()
        check_tags(self, cleaned_data)
        return cleaned_data


#同行者・気分のタグが決まった選択肢か確認する（目的地とミッションで共通）
def check_tags(form, cleaned_data):
    if cleaned_data.get("companion_tag") not in COMPANION_TAGS:
        form.add_error("companion_tag", "同行者を選択してください。")
    if cleaned_data.get("mood_tag") not in MOOD_TAGS:
        form.add_error("mood_tag", "気分を選択してください。")
