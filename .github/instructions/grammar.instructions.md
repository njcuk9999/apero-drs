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

## Long function calls (not a thin wrapper)

When a call (e.g. one whose result is unpacked into several variables) does
not fit within 80 chars, do not split the call's arguments across
continuation lines. Instead prefer, in order of preference:

1. Assign the call's result to a single variable first, then unpack:
```python
bout = module.some_function(arg1, arg2, arg3)
result1, result2, result3 = bout
```
2. If the arguments themselves are long, collect them into a list first and
   splat with `*args`, keeping the call on one line:
```python
bargs = [arg1, arg2, arg3]
result1, result2, result3 = module.some_function(*bargs)
```
3. Combine both when needed (long arguments and a call that still would not
   fit):
```python
bargs = [arg1, arg2, arg3]
bout = module.some_function(*bargs)
result1, result2, result3 = bout
```

Pick the first option that keeps every line within 80 chars.



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
into a context-named tuple and splat it:

```python
def _method_name(self, param1, param2, param3):
    helper_args = (param1, param2, param3)
    return module.helper_func(self, *helper_args)
```

Do not use bare `args`/`kwargs` for temporary delegate variables; reserve
those names for actual function inputs or parser output. Wrap the
`helper_args = (...)` assignment at 80 chars; continuation lines align to
the `(` of `helper_args = (`:

```python
def _large_method(self, alpha: str, beta: str,  gamma: str,   
                  delta: str, epsilon: str):
    helper_args = (alpha, beta, gamma, delta,
                   epsilon)
    return module.helper_func(self, *helper_args)
```

## Thin wrapper methods – forwarding keyword args

When a method forwards all non-`self` parameters **as matching keyword
arguments** (`name=name`) to a single helper, collect them with a
context-named `dict(...)` and splat with double-star expansion:

```python
def _method_name(self, param1, param2):
    helper_kwargs = dict(param1=param1, param2=param2)
    return module.helper_func(self, **helper_kwargs)
```

Wrap the `helper_kwargs = dict(...)` assignment at 80 chars; continuation
lines align to the `(` of `helper_kwargs = dict(`:

```python
def _method_name(self,  alpha, beta, gamma: bool = False,
                 delta: bool = True):
    helper_kwargs = dict(alpha=alpha, beta=beta,
                         gamma=gamma, delta=delta)
    return module.helper_func(self, **helper_kwargs)
```

## Thin wrapper methods – mixed positional and keyword args

When a method forwards some args positionally and some as kwargs, use both:

```python
def _method_name(self, pos1, pos2, key1=None, key2=True):
    helper_args = (pos1, pos2)
    helper_kwargs = dict(key1=key1, key2=key2)
    return module.helper_func(self, *helper_args, **helper_kwargs)
```

## Multi-line function signatures

When a function signature does not fit on one line, place each parameter on
its own line, indented 4 spaces from `def`:

```python
def _long_method(self, first_param: str, second_param: dict,
                third_param: bool = False) -> dict:
    ...
```