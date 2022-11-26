from urllib.parse import urlparse
from django.conf import settings
from django.template import Library

register = Library()

@register.filter(name='add_css_class_attr')
def add_css_class_attr(value, arg):
    # print 'value %s' % value
    return value.as_widget(attrs={'class': arg})

@register.filter(name='color_rate')
def color_rate(value, arg):
    
    if value == 'green':
        return value.as_widget(attrs={'class': "color-green"})
    elif value == 'yellow':
        return value.as_widget(attrs={'class': "color-yellow"})
    elif value == 'red':
        return value.as_widget(attrs={'class': "color-red"})