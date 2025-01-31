# forms.py
from django import forms

class PersonSearchForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )