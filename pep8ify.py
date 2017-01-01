#!/usr/bin/env python

import six
import traitlets
import operator
import sys
import imp
import functools
import wrapt
import inspect
import builtins
import re
import inflection
import collections
import itertools
import weakref

_sentinel = object()
_sentinel_raise = object()


_TRANS_MAP = collections.OrderedDict({
    {builtins.method}: (r'(\w[A-Z][a-z]+)': inflection.underscore),
})


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class AttrDictTree(collections.defaultdict):
    @staticmethod
    def __new__(cls, *args, **kwargs):
        # Inject our own class as the default type if not specified
        self = cls(cls, *args, **kwargs)
        return self


def _get_members(obj, predicate=None):
    for name in dir(obj):
        obj = getattr(obj, name)

        if predicate and not predicate(obj):
            continue

        yield name, obj


_Pepable = collections.namedtuple('Pepable', ['name', 'obj', 'pep_name'])


class Pepable(_Pepable):
    def __init


def is_pepable_name(name):
    return not name.islower() and '_' not in name


def pepify_name(name):
    if not is_pepable_name(name):
        raise ValueError(name)
    return inflection.underscore(name)


def get_pepable_functions_in(parent):
    add_funcs = []

    def predicate(obj):
        return inspect.ismethod(obj) or inspect.isfunction(obj)

    for name, obj in inspect.getmembers(parent, predicate):
        try:
            pname = pepify_name(name)
        except ValueError:
            continue
        add_funcs[tname] = pname
        add_funcs[tname] = obj

    return add_funcs




CAMEL = inflection.camelize
UNDERSCORE = inflection.underscore


class Adaptation(object):
    _Trans = collections.namedtuple('_Trans', ['read', 'modify', 'write'])

    def __init__(self, read=UNDERSCORE, modify=CAMEL, write=CAMEL):
        self.cache = weakref.WeakValueDictionary()
        self.trans = self._Trans(read, modify, write)

    def get_attr(self, name):
        cache = self.cache

        if name in cache:
            return cache[name]

        adapted_name = adapt.src(name)
        return getattr(self.__wrapped__, adapted_name)

    def set_attr(self, name, value):
        adapted_name = 
        return super(PepifyProxy, self).__setattr__(name, value)


class CachingPepifier(Pepify):
    def __getattr__(self, name):
        return getattr(self.__wrapped__, adapted_name)

    def __setattr__(self, name, value):
        return super(PepifyProxy, self).__setattr__(name, value)


class PepifyProxy(wrapt.ObjectProxy):

    def __init__(self, wrapped, adapt=Adaptation(CAMEL, UNDERSCORE)):
        self.__adapt = adapt
        super(PepifyProxy, self).__init__(wrapped)

    def __getattr__(self, name):
        adapt = self.__adapt
        cache = self.__cache

        if name in cache:
            return cache[name]

        adapted_name = adapt.src(name)
        return getattr(self.__wrapped__, adapted_name)

    def __setattr__(self, name, value):
        adapted_name = 
        return super(PepifyProxy, self).__setattr__(name, value)


class PepifyImporter(object):
    def find_module(self, fullname, path=None):
        """Module finding method. It tells Python to use our hook
        only for the pytz package.
        """
        if fullname == 'pytz':
            self.path = path
            return self
        return None

    def load_module(self, name):
        """Module loading method. It imports pytz normally
        and then enhances it with our generic timezones.
        """
        if name != 'pytz':
            raise ImportError("%s can only be used to import pytz!",
                              self.__class__.__name__)
        if name in sys.modules:
            return sys.modules[name]    # already imported

        file_obj, pathname, desc = imp.find_module(name, self.path)
        try:
            pytz = imp.load_module(name, file_obj, pathname, desc)
        finally:
            if file_obj:
                file_obj.close()

        pytz = self.__enhance_pytz(pytz)
        sys.modules[name] = pytz
        return pytz

    def __enhance_pytz(self, pytz):
        """Adds support for generic timezones (GMT+X) to pytz module.
        Patch includes changing all_timezones list and set, as well
        as modifying timezone() function.
        """
        generic_tz = self.__get_generic_timezones()

        # add to various collections
        pytz.generic_timezones = list(generic_tz.iterkeys())
        pytz.generic_timezones_set = set(generic_tz.iterkeys())
        pytz.all_timezones.extend(generic_tz)
        pytz.all_timezones_set = set(pytz.all_timezones) # has to be recreated

        # patch pytz.timezone()
        old__pytz_timezone = pytz.timezone
        @functools.wraps(old__pytz_timezone)
        def pytz_timezone(zone):
            try:
                return old__pytz_timezone(zone)
            except IOError: # when pytz doesn't find match in its data file
                if zone not in pytz.generic_timezones_set:
                    raise
                tz = pytz.FixedOffset(generic_tz[zone])
                pytz._tzinfo_cache[zone] = tz
                return tz
        pytz.timezone = pytz_timezone

        return pytz

    def __get_generic_timezones(self):
        """Returns dictionary mapping names of our generic
        GMT timezones to their offsets from UTC in minutes.
        """
        span = range(-12, 14 + 1)
        span.remove(0) # pytz alrady has GMT
        return dict(('GMT%(sign)s%(offset)s' % {
                        'sign': '+' if i > 0 else '-',
                        'offset': abs(i),
                     }, timedelta(hours=i).total_seconds() // 60)
                     for i in span)


_importer = PepifyImporter()

def register_import_hook(instance=PepifyImporter()):
    sys.meta_path.append(instance)

