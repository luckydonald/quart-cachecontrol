# -*- coding: utf-8 -*-
"""
    quart_cachecontrol.error
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2015 by Thomas Wiebe.
    :copyright: (c) 2023 by Luckydonald.
    :license: BSD, see LICENSE for more details.
"""


class QuartCacheControlError(Exception):
    pass


class CacheControlAttributeInvalidError(QuartCacheControlError):
    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __str__(self):
        return 'Attribute {!r} not a valid Quart Cache-Control parameter'.format(
            self.attr_name)
