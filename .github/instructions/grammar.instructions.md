---
description: Python grammar and style conventions for this codebase. Load when writing or reviewing Python code in any workspace folder.
applyTo: '**/*.py'
---

# Python Grammar Conventions

## String literals

- Favour single quotes for string literals (e.g., `'example'`) unless the string contains a single quote character, in which case use double quotes (e.g., `"example's"`).

- Only use double quotes for docstrings, following the convention of using triple double quotes for docstrings (e.g., `"""This is a docstring."""`) and inside a string (e.g. an SQL query) where double quotes are required by the syntax of the string content.


## Line length

Hard limit: **80 characters**. Wrap longer lines using Python's implicit
continuation inside parentheses. Continuation lines are indented to align
with the character immediately after the opening `(`.

When logical statements are long break up as follows:
```python
cond1 = ...
cond2 = ...
if cond1 and cond2:
    ...
```

Same for long math expressions:
```python
part1 = ...
part2 = ...
result = part1 + part2
```



## Python dictionaries

- Prefer the following:
```python
x = dict()
x['key1'] = value1
x['key2'] = value2
```

over 
```python
x = {'key1': value1, 'key2': value2}
```

or multi-line dict or `{}` dict literals, to avoid long lines and to make it easier to add/remove keys in the future.


## Thin wrapper methods – forwarding positional args

When a method does nothing except forward its non-`self` parameters
**positionally** to a single helper function, collect the forwarded values
into an `args` tuple and splat with `*args`:

```python
def _method_name(self, param1, param2, param3):
    args = (param1, param2, param3)
    return module.helper_func(self, *args)
```

Wrap the `args = (...)` assignment at 80 chars; continuation lines align to
the `(` of `args = (`:

```python
def _large_method(self, alpha: str, beta: str,  gamma: str,   
                  delta: str, epsilon: str):
    args = (alpha, beta, gamma, delta,
            epsilon)
    return module.helper_func(self, *args)
```

## Thin wrapper methods – forwarding keyword args

When a method forwards all non-`self` parameters **as matching keyword
arguments** (`name=name`) to a single helper, collect them with `kwargs =
dict(...)` and splat with `**kwargs`:

```python
def _method_name(self, param1, param2):
    kwargs = dict(param1=param1, param2=param2)
    return module.helper_func(self, **kwargs)
```

Wrap the `kwargs = dict(...)` assignment at 80 chars; continuation lines
align to the `(` of `kwargs = dict(`:

```python
def _method_name(self,  alpha, beta, gamma: bool = False,
                 delta: bool = True):
    kwargs = dict(alpha=alpha, beta=beta,
                  gamma=gamma, delta=delta)
    return module.helper_func(self, **kwargs)
```

## Thin wrapper methods – mixed positional and keyword args

When a method forwards some args positionally and some as kwargs, use both:

```python
def _method_name(self, pos1, pos2, key1=None, key2=True):
    args = (pos1, pos2)
    kwargs = dict(key1=key1, key2=key2)
    return module.helper_func(self, *args, **kwargs)
```

## Multi-line function signatures

When a function signature does not fit on one line, place each parameter on
its own line, indented 4 spaces from `def`:

```python
def _long_method(self, first_param: str, second_param: dict,
                third_param: bool = False) -> dict:
    ...
```