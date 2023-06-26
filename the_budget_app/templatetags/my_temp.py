from django import template


# To register my custom filter
register = template.Library()

@register.filter(name='abs')
def absolute(value):
    return abs(value)