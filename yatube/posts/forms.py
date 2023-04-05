from django import forms
from django.conf import settings

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control',
                                                   'rows': settings.ROWS}),
            'group': forms.Select(attrs={'class': 'form-control'})
        }
