from django import template


register = template.Library()


def get(value, arg):
    return value.get(arg).items()


register.filter('get', get)
