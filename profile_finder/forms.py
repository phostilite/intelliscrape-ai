# forms.py
from django import forms
from .models import Source

class PersonSearchForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    source = forms.ModelChoiceField(
        queryset=Source.objects.filter(is_active=True),
        required=False,
        empty_label="All Sources"
    )