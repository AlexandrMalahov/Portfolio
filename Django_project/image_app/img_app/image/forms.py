from django import forms
from .models import Images, ImageComment


class ImagesForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ('name', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = ImageComment
        fields = ('comment',)
