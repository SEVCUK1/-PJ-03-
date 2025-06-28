from datetime import datetime

from django import template

forbidden_words = ['текст', 'Текст']

register = template.Library()
@register.simple_tag
def hide_forbidden(value):
    words = value.split()
    result = []
    for word in words:
        if word in forbidden_words:
            result.append(word[0] + "*"*(len(word)-2) + word [-1])
        else:
            result.append(word)
    return " ".join(result)
