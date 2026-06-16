"""Lightweight pure-Python shim for numpy.

This project no longer relies on pandas/numpy functionality, but some
third-party packages can still try to import numpy during startup. On this
Windows environment, the binary numpy wheels are blocked by policy, so we
provide a tiny compatibility layer that satisfies imports without loading the
native extension modules.

The shim intentionally implements only a very small surface area.
If a part of the app truly needs real numpy operations later, this file should
be removed and the environment should be fixed instead.
"""

from __future__ import annotations

import builtins
import sys
import types
from typing import Any, Iterable

__version__ = "0.0.0-shim"


class ndarray(list):
    """Very small stand-in used only so isinstance checks do not explode."""


class generic:
    """Base marker class used by a few type checks."""


class dtype:
    def __init__(self, type_: Any = None):
        self.type = type_

    def __repr__(self) -> str:
        return f"dtype({self.type!r})"


bool_ = bool
int_ = int
float_ = float
complex_ = complex
bytes_ = bytes
str_ = str
number = (int, float, complex)
integer = int
floating = float


def _as_list(value: Any) -> list:
    if isinstance(value, (list, tuple, ndarray)):
        return list(value)
    return [value]


def array(value: Any, dtype: Any = None) -> ndarray:
    return ndarray(_as_list(value))


def asarray(value: Any, dtype: Any = None) -> ndarray:
    return array(value, dtype=dtype)


def zeros(shape: Any, dtype: Any = None) -> ndarray:
    if isinstance(shape, int):
        return ndarray([0 for _ in range(shape)])
    size = 1
    for dim in shape:
        size *= int(dim)
    return ndarray([0 for _ in range(size)])


def ones(shape: Any, dtype: Any = None) -> ndarray:
    if isinstance(shape, int):
        return ndarray([1 for _ in range(shape)])
    size = 1
    for dim in shape:
        size *= int(dim)
    return ndarray([1 for _ in range(size)])


def arange(start: int, stop: int | None = None, step: int = 1) -> ndarray:
    if stop is None:
        start, stop = 0, start
    return ndarray(list(range(start, stop, step)))


def linspace(start: float, stop: float, num: int = 50) -> ndarray:
    if num <= 1:
        return ndarray([float(stop)])
    step = (stop - start) / (num - 1)
    return ndarray([start + step * i for i in range(num)])


def isscalar(value: Any) -> bool:
    return not isinstance(value, (list, tuple, dict, set, ndarray))


def sum(values: Iterable[Any]) -> Any:
    return builtins.sum(values)


def mean(values: Iterable[float]) -> float:
    items = list(values)
    return builtins.sum(items) / len(items) if items else 0.0


def min(values: Iterable[Any]) -> Any:
    return builtins.min(values)


def max(values: Iterable[Any]) -> Any:
    return builtins.max(values)


def _register_module(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    sys.modules[name] = module
    return module


_core = _register_module("numpy._core")
_core.__dict__.update(
    {
        "ndarray": ndarray,
        "generic": generic,
        "dtype": dtype,
        "bool_": bool_,
        "int_": int_,
        "float_": float_,
        "complex_": complex_,
        "bytes_": bytes_,
        "str_": str_,
        "number": number,
        "integer": integer,
        "floating": floating,
    }
)
for submodule_name in ("multiarray", "overrides", "_multiarray_umath"):
    submodule = _register_module(f"numpy._core.{submodule_name}")
    setattr(_core, submodule_name, submodule)

core = _register_module("numpy.core")
core.__dict__.update(_core.__dict__)

typing = _register_module("numpy.typing")
typing.NDArray = ndarray

random = _register_module("numpy.random")
linalg = _register_module("numpy.linalg")
fft = _register_module("numpy.fft")


def __getattr__(name: str) -> Any:
    # Provide a friendly fallback for unexpected attribute access.
    raise AttributeError(
        f"numpy shim does not implement '{name}'. "
        "This project should not require real NumPy functionality."
    )
