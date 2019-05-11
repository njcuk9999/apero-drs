from collections import Iterable


# Takes a nested iterable structure and recursively flattens it to a 1d iterable
def flatten(items):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, str):
            yield from flatten(x)
        else:
            yield x
