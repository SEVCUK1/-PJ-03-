from django import forms
from django.core.exceptions import ValidationError
from django.views.generic import CreateView

from .models import Post, Response


class PostForm(forms.ModelForm):
    description = forms.CharField(min_length=20)

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'category',
            'author',
            'image',
        ]

        labels = {
            'title': 'Title',
            'text': 'Text',
            'category': ' category',
            'author': 'author',
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("description")
        title = cleaned_data.get("title")

        if title == text:
            raise ValidationError(
                "Заголовок не должен совпадать с текстом."
            )

        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data["name"]
        if name[0].islower():
            raise ValidationError(
                "Название должно начинаться с заглавной буквы"
            )
        return name

    def __str__(self):
        return self.user.username


class RespondForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']  # Только поле текста отклика
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }


class ResponsesFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(ResponsesFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявление',
            queryset=Post.objects.filter(author_id=user.id).order_by('-dateCreation').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )