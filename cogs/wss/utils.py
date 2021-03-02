from __future__ import annotations

import asyncio
import json
from asyncio import Semaphore, as_completed
from asyncio.futures import isfuture
from itertools import chain
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from discord.utils import maybe_coroutine

__all__ = (
    "bounded_gather",
    "bounded_gather_iter",
    "deduplicate_iterables",
    "AsyncIter",
)

_T = TypeVar("_T")
_S = TypeVar("_S")

# Benchmarked to be the fastest method.
def deduplicate_iterables(*iterables):
    """
    Returns a list of all unique items in ``iterables``, in the order they
    were first encountered.
    """
    # dict insertion order is guaranteed to be preserved in 3.6+
    return list(dict.fromkeys(chain.from_iterable(iterables)))


# https://github.com/PyCQA/pylint/issues/2717
class AsyncFilter(
    AsyncIterator[_T], Awaitable[List[_T]]
):  # pylint: disable=duplicate-bases
    """Class returned by `async_filter`. See that function for details.

    We don't recommend instantiating this class directly.
    """

    def __init__(
        self,
        func: Callable[[_T], Union[bool, Awaitable[bool]]],
        iterable: Union[AsyncIterable[_T], Iterable[_T]],
    ) -> None:
        self.__func: Callable[[_T], Union[bool, Awaitable[bool]]] = func
        self.__iterable: Union[AsyncIterable[_T], Iterable[_T]] = iterable

        # We assign the generator strategy based on the arguments' types
        if isinstance(iterable, AsyncIterable):
            if asyncio.iscoroutinefunction(func):
                self.__generator_instance = self.__async_generator_async_pred()
            else:
                self.__generator_instance = self.__async_generator_sync_pred()
        elif asyncio.iscoroutinefunction(func):
            self.__generator_instance = self.__sync_generator_async_pred()
        else:
            raise TypeError(
                "Must be either an async predicate, an async iterable, or both."
            )

    async def __sync_generator_async_pred(self) -> AsyncIterator[_T]:
        for item in self.__iterable:
            if await self.__func(item):
                yield item

    async def __async_generator_sync_pred(self) -> AsyncIterator[_T]:
        async for item in self.__iterable:
            if self.__func(item):
                yield item

    async def __async_generator_async_pred(self) -> AsyncIterator[_T]:
        async for item in self.__iterable:
            if await self.__func(item):
                yield item

    async def __flatten(self) -> List[_T]:
        return [item async for item in self]

    def __aiter__(self):
        return self

    def __await__(self):
        # Simply return the generator filled into a list
        return self.__flatten().__await__()

    def __anext__(self) -> Awaitable[_T]:
        # This will use the generator strategy set in __init__
        return self.__generator_instance.__anext__()


def async_filter(
    func: Callable[[_T], Union[bool, Awaitable[bool]]],
    iterable: Union[AsyncIterable[_T], Iterable[_T]],
) -> AsyncFilter[_T]:
    """Filter an (optionally async) iterable with an (optionally async) predicate.

    At least one of the arguments must be async.
    """
    return AsyncFilter(func, iterable)


async def async_enumerate(
    async_iterable: AsyncIterable[_T], start: int = 0
) -> AsyncIterator[Tuple[int, _T]]:
    """Async iterable version of `enumerate`."""
    async for item in async_iterable:
        yield start, item
        start += 1


async def _sem_wrapper(sem, task):
    async with sem:
        return await task


def bounded_gather_iter(
    *coros_or_futures, limit: int = 4, semaphore: Optional[Semaphore] = None
) -> Iterator[Awaitable[Any]]:
    """
    An iterator that returns tasks as they are ready, but limits the
    number of tasks running at a time.
    """
    loop = asyncio.get_running_loop()

    if semaphore is None:
        if not isinstance(limit, int) or limit <= 0:
            raise TypeError("limit must be an int > 0")

        semaphore = Semaphore(limit)

    pending = []

    for cof in coros_or_futures:
        if isfuture(cof) and cof._loop is not loop:
            raise ValueError("futures are tied to different event loops")

        cof = _sem_wrapper(semaphore, cof)
        pending.append(cof)

    return as_completed(pending)


def bounded_gather(
    *coros_or_futures,
    return_exceptions: bool = False,
    limit: int = 4,
    semaphore: Optional[Semaphore] = None,
) -> Awaitable[List[Any]]:
    """
    A semaphore-bounded wrapper to :meth:`asyncio.gather`.
    """
    loop = asyncio.get_running_loop()

    if semaphore is None:
        if not isinstance(limit, int) or limit <= 0:
            raise TypeError("limit must be an int > 0")

        semaphore = Semaphore(limit)

    tasks = (_sem_wrapper(semaphore, task) for task in coros_or_futures)

    return asyncio.gather(*tasks, return_exceptions=return_exceptions)


class AsyncIter(
    AsyncIterator[_T], Awaitable[List[_T]]
):  # pylint: disable=duplicate-bases
    """Asynchronous iterator yielding items from ``iterable``
    that sleeps for ``delay`` seconds every ``steps`` items.
    """

    def __init__(
        self, iterable: Iterable[_T], delay: Union[float, int] = 0, steps: int = 1
    ) -> None:
        if steps < 1:
            raise ValueError("Steps must be higher than or equals to 1")
        self._delay = delay
        self._iterator = iter(iterable)
        self._i = 0
        self._steps = steps
        self._map = None

    def __aiter__(self) -> AsyncIter[_T]:
        return self

    async def __anext__(self) -> _T:
        try:
            item = next(self._iterator)
        except StopIteration:
            raise StopAsyncIteration
        if self._i == self._steps:
            self._i = 0
            await asyncio.sleep(self._delay)
        self._i += 1
        return await maybe_coroutine(self._map, item) if self._map is not None else item

    def __await__(self) -> Generator[Any, None, List[_T]]:
        return self.flatten().__await__()

    async def next(self, default: Any = ...) -> _T:
        try:
            value = await self.__anext__()
        except StopAsyncIteration:
            if default is ...:
                raise
            value = default
        return value

    async def flatten(self) -> List[_T]:
        return [item async for item in self]

    def filter(
        self, function: Callable[[_T], Union[bool, Awaitable[bool]]]
    ) -> AsyncFilter[_T]:
        return async_filter(function, self)

    def enumerate(self, start: int = 0) -> AsyncIterator[Tuple[int, _T]]:
        return async_enumerate(self, start)

    async def without_duplicates(self) -> AsyncIterator[_T]:
        _temp = set()
        async for item in self:
            if item not in _temp:
                yield item
                _temp.add(item)
        del _temp

    async def find(
        self,
        predicate: Callable[[_T], Union[bool, Awaitable[bool]]],
        default: Optional[Any] = None,
    ) -> AsyncIterator[_T]:
        while True:
            try:
                elem = await self.__anext__()
            except StopAsyncIteration:
                return default
            ret = await maybe_coroutine(predicate, elem)
            if ret:
                return elem

    def map(self, func: Callable[[_T], Union[_S, Awaitable[_S]]]) -> AsyncIter[_S]:
        if not callable(func):
            raise TypeError("Mapping must be a callable.")
        self._map = func
        return self
