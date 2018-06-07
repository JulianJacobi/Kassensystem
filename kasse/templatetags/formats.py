from django import template

register = template.Library()


def float_filter(money):
    return float(money)


register.filter('float', float_filter)
