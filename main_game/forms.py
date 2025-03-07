from django import forms
from django.forms import ModelForm

from .models import Lesson


class LessonForm(ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "form-control"
        self.fields["text"].widget.attrs["class"] = "form-control"
        self.fields["audio"].required = False
        self.fields["english_audio"].required = False
        self.fields["image"].required = False
        self.fields["image"].widget.attrs["capture"] = "camera"
        self.fields["image"].widget.attrs["accept"] = "image/*"

    class Meta:
        model = Lesson
        fields = "__all__"


class AudioForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields["audio"].required = False
        self.fields["english_audio"].required = False

    class Meta:
        model = Lesson
        fields = ["audio", "english_audio"]
