import wrapt
import weakref
from .util import _sentinel, lazyproperty
from .adapters import camelize


class Adaptation(object):

    def __init__(self, read):
        self.read = read

    def get_attr(self, name, wrapped):
        for adapted_name in self.read(name):
            try:
                return getattr(wrapped, adapted_name)
            except AttributeError:
                # sugar
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
            # pass here to not chain exceptions
            pass
        val = super(CachingAdaptation, self).get_attr(name, wrapped)
        self.cache[name] = val
        return val


class PepifyProxy(wrapt.ObjectProxy):

    def __init__(self, wrapped, read=camelize):
        super(PepifyProxy, self).__init__(wrapped)
        self.__adapter = CachingAdaptation(read=read)

    def __getattr__(self, name):
        try:
            return super(PepifyProxy, self).__getattr__(name)
        except AttributeError:
            # pass here to not chain exceptions
            pass
        return self.__adapter.get_attr(name, wrapped=self.__wrapped__)
