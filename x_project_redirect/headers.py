__all__ = ['cache', 'cookie', 'csp', 'not_robot']
import asyncio
import functools
from datetime import datetime, timedelta
import time
from uuid import uuid4
from aiohttp import web, hdrs
from aiohttp.abc import AbstractView

from x_project_redirect.user_agents import simple_parse


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


def cookie(name='yottos_unique_id', domain='.yottos.com', days=365):
    def wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            expires = datetime.utcnow() + timedelta(days=days)
            user_cookie_expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
            user_cookie_max_age = 60 * 60 * 24 * days
            # Supports class based views see web.View
            if isinstance(args[0], AbstractView):
                request = args[0].request
            else:
                request = args[-1]
            user_cookie = request.cookies.get(name, str(time.time()).replace('.', ''))
            if isinstance(args[0], AbstractView):
                args[0].request.user_cookie = user_cookie
            else:
                args[-1].user_cookie = user_cookie
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)
            context = yield from coro(*args)
            if isinstance(context, web.StreamResponse):
                context.set_cookie(name, user_cookie,
                                   expires=user_cookie_expires,
                                   domain=domain,
                                   max_age=user_cookie_max_age)
            return context
        return wrapped
    return wrapper


def csp():
    def wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            if isinstance(args[0], AbstractView):
                request = args[0].request
            else:
                request = args[-1]
            nonce = uuid4().hex
            request.nonce = nonce
            host = request.host
            csp = []
            csp_data = {
                'base-uri': [host],
                'default-src': [host],
                'img-src': [],
                'script-src': ["'unsafe-inline'", "'nonce-%s'" % nonce, host],
                'connect-src': [host],
                'style-src': [],
                'worker-src': [],
                'frame-src': [],
                'manifest-src': [],
                'media-src': [],
                'font-src': [],
                'child-src': [],
                'form-action': [],
                'object-src': [],
                'sandbox': ['allow-scripts', 'allow-same-origin', 'allow-forms', 'allow-popups',
                            'allow-popups-to-escape-sandbox'],

            }
            if request.app['config']['debug']['console']:
                csp_data['script-src'].append("'self'")
                csp_data['style-src'].append("'self'")
                csp_data['img-src'].append("'self'")
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)
            context = yield from coro(*args)
            if isinstance(context, web.StreamResponse):
                for key, value in csp_data.items():
                    if len(value) == 0:
                        value.append("'none'")
                    csp.append('%s %s' % (key, ' '.join(value)))
                csp.append('block-all-mixed-content')
                context.headers['content-security-policy'] = '; '.join(csp)
                return context
            return context
        return wrapped
    return wrapper


def detect_device():
    def wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            if isinstance(args[0], AbstractView):
                args[0].request.device = simple_parse(args[0].request.headers[hdrs.USER_AGENT])
            else:
                args[-1].device = simple_parse(args[-1].headers[hdrs.USER_AGENT])

            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)

            context = yield from coro(*args)
            return context
        return wrapped
    return wrapper


def not_robot():
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
                context.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive, notranslate, noimageindex'
                return context
            return context
        return wrapped
    return wrapper
