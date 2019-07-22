from django import forms
from .models import DDS, DTF


class DDSForm(forms.ModelForm):
    class Meta:
        model = DDS
        fields = ('project', 'file',)
        widgets = {'project': forms.HiddenInput()}


class DTFForm(forms.ModelForm):
    class Meta:
        model = DTF
        fields = ('project', 'file',)
        widgets = {'project': forms.HiddenInput()}
