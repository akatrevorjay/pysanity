#!/usr/bin/env python
import wrapt
import re
import weakref

_sentinel = object()


def lazyproperty(fn):
    """
    Lazy/Cached property.
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazyprop


def underscore(word):
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
    word = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', word)
    word = word.replace("-", "_")
    yield word.lower()


def camelize(string, uppercase_first_letter=True):
    ret = re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)
    if uppercase_first_letter:
        yield ret
    yield ret[0].lower() + ret[1:]


class Adaptation(object):

    def __init__(self, read):
        self.read = read

    def get_attr(self, name, wrapped):
        for adapted_name in self.read(name):
            if hasattr(wrapped, adapted_name):
                return getattr(wrapped, adapted_name)

        raise AttributeError(name)


class CachingAdaptation(Adaptation):

    @lazyproperty
    def cache(self):
        return weakref.WeakValueDictionary()

    @wrapt.decorator
    def _cache_method(fn, instance, args, kwargs):
        name = args[0]

        if name in instance.cache:
            return instance.cache[name]

        val = fn(*args, **kwargs)

        instance.cache[name] = val
        return val

    get_attr = _cache_method(Adaptation.get_attr)


class PepifyProxy(wrapt.ObjectProxy):

    def __init__(self, wrapped, adapt=CachingAdaptation(read=camelize)):
        super(PepifyProxy, self).__init__(wrapped)
        self.__adapt = adapt

    def __getattr__(self, name):
        if hasattr(self.__wrapped__, name):
            return super(PepifyProxy, self).__getattr__(name)

        return self.__adapt.get_attr(name, wrapped=self.__wrapped__)
