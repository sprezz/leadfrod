# -*- coding:utf-8 -*-
from urllib import quote as quote_func

from django import template


register = template.Library()


@register.filter
def quote(s):
    return quote_func(s)
