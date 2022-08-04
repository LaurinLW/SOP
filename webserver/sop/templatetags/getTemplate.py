from django import template
from sop.models import AlgorithmModel


register = template.Library()


def get(value, arg):
    """ Custom Django Template
    """
    return value.get(f'{AlgorithmModel.objects.get(pk=int(arg)).modul_name}.{AlgorithmModel.objects.get(pk=int(arg)).class_name}').items()


register.filter('get', get)
