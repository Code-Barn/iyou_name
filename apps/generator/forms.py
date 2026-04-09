from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import GedcomFile


class GedcomUploadForm(forms.ModelForm):
    class Meta:
        model = GedcomFile
        fields = ("file",)


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]
