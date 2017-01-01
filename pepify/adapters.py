import re


def underscore(string):
    string = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', string)
    string = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', string)
    string = string.replace("-", "_")
    yield string.lower()


def camelize(string, uppercase_first_letter=True):
    ret = re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), string)
    if uppercase_first_letter:
        yield ret
    yield ret[0].lower() + ret[1:]
