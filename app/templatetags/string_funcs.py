from django import template

register = template.Library()

@register.filter(name='cutFirstLine')
def cutFirstLine(value, max_length):
    split = value.split('\n')
    return "..." + split[0][0:min(len(split[0]), max_length)]
