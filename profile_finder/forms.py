# forms.py
from django import forms

class PersonSearchForm(forms.Form):
    SOURCES = [
        ('', 'All Sources'),
        ('LinkedIn', 'LinkedIn'),
        ('Twitter', 'Twitter'),
        ('Facebook', 'Facebook'),
        ('GitHub', 'GitHub'),
        ('Medium', 'Medium'),
        ('Wikipedia', 'Wikipedia'),
    ]

    name = forms.CharField(max_length=200)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    source = forms.ChoiceField(
        choices=SOURCES,
        required=False,
        initial=''
    )