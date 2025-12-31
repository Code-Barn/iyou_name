from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import GedcomFile


class GedcomUploadForm(forms.ModelForm):
    class Meta:
        model = GedcomFile
        fields = ("file",)


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
