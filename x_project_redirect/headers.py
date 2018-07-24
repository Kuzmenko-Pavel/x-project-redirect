__all__ = ['cache']
import asyncio
import functools
from aiohttp import web, hdrs


def cache():
    def wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)
            context = yield from coro(*args)
            if isinstance(context, web.StreamResponse):
                context.headers[hdrs.CACHE_CONTROL] = 'must-revalidate, max-age=0'
            return context
        return wrapped
    return wrapper