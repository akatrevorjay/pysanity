import weakref

from .util import _sentinel, lazyproperty


class Adaptation(object):

    def __init__(self, read):
        self.read = read

    def get_attr(self, name, wrapped):
        for adapted_name in self.read(name):
            try:
                return getattr(wrapped, adapted_name)
            except AttributeError:
                continue

        raise AttributeError(name)


class CachingAdaptation(Adaptation):

    @lazyproperty
    def cache(self):
        return weakref.WeakValueDictionary()

    def get_attr(self, name, wrapped):
        try:
            return self.cache[name]
        except KeyError:
            val = super(CachingAdaptation, self).get_attr(name, wrapped)
            self.cache[name] = val
            return val
