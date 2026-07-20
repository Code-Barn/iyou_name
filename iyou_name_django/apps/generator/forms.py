from django import forms

from .models import GedcomFile


class GedcomUploadForm(forms.ModelForm):
    class Meta:
        model = GedcomFile
        fields = ("file",)
