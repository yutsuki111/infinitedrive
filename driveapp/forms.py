from django import forms

class LoginForm(forms.Form):
    # クラス変数を定義
    name = forms.CharField(label='お名前')
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='件名')
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    # 初期化メソッド
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ラベルの末尾の「:」を消去
        self.label_suffix = ""

        self.fields['name'].widget.attrs['placeholder'] = 'お名前を入力してください'
        self.fields['name'].widget.attrs['class'] = 'form-control'

        self.fields['title'].widget.attrs['placeholder'] = 'タイトルを入力してください'
        self.fields['title'].widget.attrs['class'] = 'form-control'

        self.fields['email'].widget.attrs['placeholder'] = 'メールアドレスを入力してください'
        self.fields['email'].widget.attrs['class'] = 'form-control'

        self.fields['message'].widget.attrs['placeholder'] = 'メッセージを入力してください'
        self.fields['message'].widget.attrs['class'] = 'form-control'