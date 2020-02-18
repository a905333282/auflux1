# -*- coding: utf-8 -*-


from .item import *


def all():
    result = []
    models = [item]
    for m in models:
        result += m.__all__
    return result


__all__ = all()
