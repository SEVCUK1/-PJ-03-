from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    USER_CATEGORY = (('Tank', 'Танк'),
                     ('Healer', 'Хил'),
                     ('Damage_Dealer', 'ДД'),
                     ('Merchant', 'Торговец'),
                     ('Guild_Master', 'Гильдмастер'),
                     ('Quest_Giver', 'Квестгивер'),
                     ('Blacksmith', 'Кузнец'),
                     ('Leatherworker', 'Кожевник'),
                     ('Potions_Master', 'Зельевар'),
                     ('Spell_Master', 'Мастер заклинаний'))
    category = models.CharField(max_length=32, choices=USER_CATEGORY, verbose_name='Категория')
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name='Изображение')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __str__(self):
        return self.title


class Response(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст')
    ad = models.ForeignKey(Post, on_delete=models.CASCADE)
    message = models.TextField(default="Нет сообщения")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Response for {self.ad.title} by {self.user.username}"
