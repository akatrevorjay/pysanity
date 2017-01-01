import inspect
import weakref
import wrapt
from .util import _sentinel, lazyproperty
from .adapters import camelize


class Adapter(object):

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


class CachedAdapter(Adapter):

    @lazyproperty
    def cache(self):
        return weakref.WeakValueDictionary()

    def get_attr(self, name, wrapped):
        try:
            return self.cache[name]
        except KeyError:
            # pass here to not chain exceptions
            pass
        val = super(CachedAdapter, self).get_attr(name, wrapped)
        self.cache[name] = val
        return val


class PepifyProxy(wrapt.ObjectProxy):

    def __init__(self, wrapped, adapter):
        super(PepifyProxy, self).__init__(wrapped)
        self._self_adapter = adapter

    def __getattr__(self, name):
        try:
            return super(PepifyProxy, self).__getattr__(name)
        except AttributeError:
            # pass here to not chain exceptions
            pass
        return self._self_adapter.get_attr(name, wrapped=self.__wrapped__)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, repr(self.__wrapped__))


class RecursivePepifyProxy(PepifyProxy):

    def __init__(self, wrapped, adapter, should_recurse=(inspect.isclass, inspect.ismodule)):
        super(RecursivePepifyProxy, self).__init__(wrapped, adapter)
        self._self_should_recurse = should_recurse

    def __getattr__(self, name):
        val = super(RecursivePepifyProxy, self).__getattr__(name)

        for check in self._self_should_recurse:
            if check(val):
                return RecursivePepifyProxy(val, self._self_adapter, should_recurse=self._self_should_recurse)

        return val


def proxy(wrapped, read=camelize, cache=True, recurse=True):
    adapter_factory = cache and CachedAdapter or Adapter
    proxy_factory = recurse and RecursivePepifyProxy or PepifyProxy

    adapter = adapter_factory(read=read)
    return proxy_factory(wrapped, adapter)
