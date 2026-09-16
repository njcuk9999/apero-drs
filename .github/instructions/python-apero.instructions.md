---
description: "Use when editing or generating Python code. Enforce a hard maximum line length of 80 characters in all Python files."
name: "General Python Rules"
applyTo: "**/*.py"
---
# Python Line Length

- Keep every line in Python files at 80 characters or fewer.
- Prefer wrapping long expressions across multiple lines rather than
  shortening names.
- Wrap imports, function signatures, call arguments, and long strings so each
  resulting line stays within 80 characters.
- Preserve behavior when reflowing lines.


# Python line wrapping

- Wrap using parentheses where possible, rather than backslashes
- Never use a trailing backslash (`\`) line continuation, for any
  statement (including unpacking assignments) - restructure the code
  (e.g. via an intermediate `outs = ...` variable) instead
- Do not break after binary operators; instead, break before them to improve readability
- When breaking after an open parenthesis, indent the continued line to align with the first character after the open parenthesis on the previous line
- When breaking before a binary operator, indent the continued line to align with the operator on the previous line
- For long strings, break after a logical point (e.g., after a comma or before a conjunction) and use implicit string concatenation with parentheses to maintain readability

# Delegate call style

- For long delegated calls (for example to `_impls.*` or to
  `aperocore.science.*_core` modules) avoid large multiline argument blocks
  directly in the call.
- Prefer collecting positional arguments into an `args` list and then calling
  with splat expansion:
```python
args = [arg1, arg2, arg3]
return _impls.some_delegate(self, *args)
```
- For keyword arguments, prefer collecting them into a `kwargs` dict and then
  calling with double-splat expansion:
```python
kwargs = {'kwarg1': value1, 'kwarg2': value2}
return _impls.some_delegate(self, **kwargs)
```
- When a delegated call returns a tuple that must be unpacked and the call
  itself does not fit on one line, assign the whole return value to a single
  variable (`outs`, or `args`/`kwargs` if clearer) on its own line, then
  unpack it on the next line - do not wrap the call across lines with a
  backslash:
```python
args = [arg1, arg2, arg3]
kwargs = dict(kwarg1=value1)
outs = module.function(*args, **kwargs)
out1, out2, out3 = outs
```

# Commentation

- Try to comment most lines - if a line is doing something non-obvious, add a comment above it explaining why.
- Add description docstrings to all functions, classes, and modules, describing their purpose, parameters, return values, and any exceptions raised.

# Importing

- Avoid wildcard imports (e.g., `from module import *`) to prevent namespace pollution and improve code readability.
- Group imports in the following order: standard library imports, third-party imports, and local application/library imports. Each group should be separated by a blank line.
- Do not import single functions when multiple functions are used from the same module; instead, import the entire module and use dot notation to access its functions (e.g., `import math` and then `math.sqrt()` instead of `from math import sqrt`).
- Avoid parenthesized imports (e.g., `from module import (function1, function2)`) unless necessary for line length; prefer separate import statements for clarity.

# Code layout

- Start each python file with:
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
```
- Use 4 spaces per indentation level.
- Limit all lines to a maximum of 80 characters.
- Use blank lines to separate top-level function and class definitions
- constants should be defined at the top of the file, after imports and before any function or class definitions.

- Prefer sections as follows:
```python

# =============================================================================
# Define variables
# =============================================================================

# =============================================================================
# Define classes
# =============================================================================

# =============================================================================
# Define functions
# =============================================================================

# =============================================================================
# Define worker functions
# =============================================================================

# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================
```

- worker function section can be not used if not needed
- classes section can be not used if no classes defined
- the __main__ section should be minimal (used for testing or running code,
with a call to a main function that does the work) and should be at the end of the file.
