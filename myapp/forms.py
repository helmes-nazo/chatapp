from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordChangeForm
)

from .models import CustomUser, Talk

User = get_user_model()


class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "icon")


class LoginForm(AuthenticationForm):
    pass

class TalkForm(forms.ModelForm):
    class Meta:
        model = Talk
        fields = ("talk",)
        widgets = {"talk": forms.TextInput(attrs={"autocomplete": "off"})}

class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username']

class CustomEmailInput(forms.EmailInput):
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

class ChangeEmailForm(forms.ModelForm):
    email_confirm = forms.EmailField(label='メールアドレス（確認用）', widget=CustomEmailInput(), required=False)

    class Meta:
        model = get_user_model()
        fields = ['email', 'email_confirm']
        widgets = {
            'email': CustomEmailInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_confirm = cleaned_data.get("email_confirm")

        if email and email != email_confirm:
            raise forms.ValidationError("メールアドレスが一致しません。")

        return cleaned_data
    

class ChangeIconForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['icon']

class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['old_password', 'new_password1', 'new_password2']:
            self.fields[fieldname].help_text = None