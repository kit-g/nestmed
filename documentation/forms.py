from django import forms
from .models import Transcript


class TranscriptForm(forms.ModelForm):
    class Meta:
        model = Transcript
        fields = ['text', 'audio_file']

    text = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': 'Optional text'}))
    audio_file = forms.FileField(required=False)
