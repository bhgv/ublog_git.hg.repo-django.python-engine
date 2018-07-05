# -*- coding: utf-8 -*-
import re
from datetime import datetime
from my_django import template

register = template.Library()


@register.filter
def shorten_sha1(sha1):
    if re.match('[a-z\d]{20,40}', sha1):
        sha1 = sha1[:10]
    return sha1

@register.filter
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp)

@register.filter
def bytes_to_str(bytes_value):
    return bytes_value.decode()