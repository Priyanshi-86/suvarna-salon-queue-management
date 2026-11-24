from django import template
from django.utils.html import format_html
register = template.Library()

@register.filter
def loc(obj, field):
    g = lambda l: getattr(obj, f"{field}_{l}")
    return format_html('<span data-en="{}" data-hi="{}" data-gu="{}">{}</span>', g("en"), g("hi"), g("gu"), g("en"))
