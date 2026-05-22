from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q

from users.models import User
from users.validators import normalize_phone, validate_github_url, validate_phone_format


class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=124, label="Имя")
    surname = forms.CharField(max_length=124, label="Фамилия")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(self.request, email=email, password=password)
            if user is None:
                raise forms.ValidationError(
                    "Неверный email или пароль",
                    code="invalid_login",
                )
            cleaned_data["user"] = user
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["avatar"].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if not phone:
            raise forms.ValidationError("Укажите номер телефона.")
        phone = validate_phone_format(phone)
        normalized = normalize_phone(phone)
        alt_phone = (
            f"8{normalized[2:]}"
            if normalized.startswith("+7")
            else f"+7{normalized[1:]}"
        )
        duplicate = User.objects.filter(
            Q(phone=normalized) | Q(phone=alt_phone)
        ).exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError("Этот номер телефона уже используется.")
        return normalized

    def clean_github_url(self):
        return validate_github_url(self.cleaned_data.get("github_url"))

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("avatar"):
            user.avatar = self.cleaned_data["avatar"]
        if commit:
            user.save()
        return user


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Текущий пароль",
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Новый пароль",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Подтвердите новый пароль",
    )