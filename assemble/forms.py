from django import forms
from django.forms import fields
from .models import URL,BigTag,Report

class URLForm(forms.ModelForm):
    class Meta:
        model = URL
        fields=('url',)

class BigTagForm(forms.ModelForm):
    class Meta:
        model = BigTag
        fields = ('tag',)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('report','text',)