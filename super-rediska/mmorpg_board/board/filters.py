import django_filters
from django import forms
from .models import Post

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок'
    )

    category = django_filters.ChoiceFilter(
        choices=Post.USER_CATEGORY,
        label='Категории',
        empty_label='Выберите категорию',
    )

    dateCreation_after = django_filters.DateTimeFilter(
        field_name='dateCreation',
        lookup_expr='gt',
        label='Дата',
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = Post  # Указываем модель для фильтрации
        fields = ['title', 'category', 'dateCreation_after']