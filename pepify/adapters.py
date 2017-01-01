import re
import functools


RE_SNAKE_CASE = [
    functools.partial(
        re.compile(r'(.)([A-Z][a-z]+)').sub,
        r'\1_\2',
    ),
    functools.partial(
        re.compile('([a-z0-9])([A-Z])').sub,
        r'\1_\2',
    ),
]

RE_UPPER_CAMEL_CASE = functools.partial(
    re.compile(r"(?:^|_)(.)").sub,
    lambda m: m.group(1).upper(),
)


def snake_case(string):
    for f in RE_SNAKE_CASE:
        string = f(string)
    string = string.replace("-", "_")
    yield string.lower()


def is_snake_case(string):
    string = string.replace('_', '')
    return string.islower() and string.isalnum()


def upper_camel_case(string):
    yield RE_UPPER_CAMEL_CASE(string)


def is_upper_camel_case(string):
    return string.isalnum() and string[0].isupper()


def lower_camel_case(string):
    first = string[0].lower()
    for s in upper_camel_case(string):
        yield first + s[1:]


def is_lower_camel_case(string):
    return string.isalnum() and string[0].isupper()


def all_camel_case(string):
    for s in upper_camel_case(string):
        if s[0].isupper():
            yield s[0].lower() + s[1:]
        yield s


def is_all_camel_case(string):
    return string.isalnum()
