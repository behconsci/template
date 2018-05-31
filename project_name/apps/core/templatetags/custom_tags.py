# -*- coding: utf-8 -*-
import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def append_pagination(path, page):
    if '?' in path:
        if 'page' in path:
            return re.sub(r'page=(\d+)', 'page=%s' % page, path)
        else:
            return '%s&page=%s' % (path, page)
    else:
        return '%s?page=%s' % (path, page)


@register.simple_tag
def define(value=None):
    return value


@register.filter
@stringfilter
def count_list(words):
    words_list = words.split(',')
    return len(words_list)


@register.simple_tag
def dynamic_class(number):
    if number > 3:
        return 'col-xs-6 col-md-4 col-lg-3'

    if number == 3:
        return 'col-xs-6 col-md-4 col-lg-4'

    if number == 2:
        return 'col-xs-6 col-md-4 col-lg-6'

    if number == 1:
        return 'col-xs-12 col-md-12 col-lg-12'

