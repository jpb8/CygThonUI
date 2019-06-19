from django import forms
from .models import DDS


class DDSForm(forms.ModelForm):
    class Meta:
        model = DDS
        fields = ('project', 'file',)
