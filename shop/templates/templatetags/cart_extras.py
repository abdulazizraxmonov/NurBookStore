# your_app/templatetags/cart_extras.py

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except TypeError:
        return ''
