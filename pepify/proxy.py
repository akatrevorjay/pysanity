import inspect
import operator
import weakref
import wrapt
from .util import _sentinel, lazyproperty
from . import adapters


class Adapter(object):

    def __init__(self, get, predicate=None):
        self.get = get
        self.predicate = predicate

    def find_attr(self, name, wrapped, predicate=None):
        if not predicate:
            predicate = self.predicate

        for adapted_name in self.get(name):
            try:
                obj = getattr(wrapped, adapted_name)
            except AttributeError:
                continue
            if not predicate or predicate(name, adapted_name, obj):
                return obj

        raise AttributeError(name)


class CachedAdapter(Adapter):

    @lazyproperty
    def cache(self):
        return weakref.WeakValueDictionary()

    def find_attr(self, name, wrapped, predicate=None):
        try:
            return self.cache[name]
        except KeyError:
            val = super(CachedAdapter, self).find_attr(name, wrapped, predicate)

            self.cache[name] = val
            return val


class PepifyProxy(wrapt.ObjectProxy):
    def __init__(self, wrapped, adapter):
        super(PepifyProxy, self).__init__(wrapped)
        self._self_adapter = adapter

    @property
    def __get__(self):
        return self.__wrapped__.__get__

    @property
    def __call__(self):
        return self.__wrapped__.__call__

    def __getattr__(self, name):
        try:
            return super(PepifyProxy, self).__getattr__(name)
        except AttributeError:
            # pass here to not chain exceptions
            pass
        return self._self_adapter.find_attr(name, wrapped=self.__wrapped__)

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


def obj_is_function_or_method(name, adapted_name, obj):
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def make_proxy(wrapped, get=adapters.lower_camel_case, predicate=obj_is_function_or_method, cache=True, recurse=True):
    adapter_factory = cache and CachedAdapter or Adapter
    proxy_factory = recurse and RecursivePepifyProxy or PepifyProxy

    adapter = adapter_factory(get=get, predicate=predicate)
    return proxy_factory(wrapped, adapter)
