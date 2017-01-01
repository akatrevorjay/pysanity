import wrapt

from .adaptation import CachingAdaptation
from .adapters import camelize


class PepifyProxy(wrapt.ObjectProxy):

    def __init__(self, wrapped, read=camelize):
        super(PepifyProxy, self).__init__(wrapped)
        self.__adapter = CachingAdaptation(read=read)

    def __getattr__(self, name):
        try:
            return super(PepifyProxy, self).__getattr__(name)
        except AttributeError:
            return self.__adapter.get_attr(name, wrapped=self.__wrapped__)
