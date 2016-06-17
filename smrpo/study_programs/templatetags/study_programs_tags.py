from django import template

register = template.Library()


def to_percent(val):
    return str(val * 100)

def divide_with_two(val):
    return str(val/2)

register.filter('divide_with_two', divide_with_two)
register.filter('to_percent', to_percent)
