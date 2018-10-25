from aiohttp import hdrs, web
import time
import re
from datetime import datetime, timedelta

from x_project_redirect.logger import logger, exception_message


ip_regex = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')


async def handle_404(request, response):
    return web.Response(text='')


async def handle_405(request, response):
    return web.Response(text='')


async def handle_500(request, response):
    return web.Response(text='')


def error_pages(overrides):
    async def middleware(app, handler):
        async def middleware_handler(request):
            try:
                response = await handler(request)
                override = overrides.get(response.status)
                if override is None:
                    return response
                else:
                    return await override(request, response)
            except web.HTTPException as ex:
                # if ex.status not in [404, 405]:
                #     logger.error(exception_message(exc=str(ex), request=str(request._message)))
                # else:
                #     logger.warning(exception_message(exc=str(ex), request=str(request._message)))
                override = overrides.get(ex.status)
                if override is None:
                    raise
                else:
                    return await override(request, ex)

        return middleware_handler

    return middleware


async def cookie_middleware(app, handler):
    async def middleware(request):
        user_cookie_name = 'yottos_unique_id'
        expires = datetime.utcnow() + timedelta(days=365)
        user_cookie_expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
        user_cookie_domain = '.yottos.com'
        user_cookie_max_age = 60*60*24*365
        request.user_cookie = request.cookies.get(user_cookie_name, str(time.time()).replace('.', ''))
        response = await handler(request)
        response.set_cookie(user_cookie_name, request.user_cookie,
                            expires=user_cookie_expires,
                            domain=user_cookie_domain,
                            max_age=user_cookie_max_age)
        return response

    return middleware


async def ip_middleware(app, handler):
    async def middleware(request):
        host = '127.0.0.1'
        x_real_ip = request.headers.get('X-Real-IP', request.headers.get('X-Forwarded-For', ''))
        x_real_ip_check = ip_regex.match(x_real_ip)
        if x_real_ip_check:
            x_real_ip = x_real_ip_check.group()
        else:
            x_real_ip = None
        if x_real_ip:
            host = x_real_ip
        else:
            try:
                peername = request.transport.get_extra_info('peername')
                if peername and isinstance(peername, tuple):
                    host, _ = peername
            except Exception as ex:
                logger.error(exception_message(exc=str(ex), request=str(request._message)))
        request.ip = host
        response = await handler(request)
        return response

    return middleware


async def referer_middleware(app, handler):
    async def middleware(request):
        headers = request.headers
        request.referer = headers.get('Referer', '')
        response = await handler(request)
        return response

    return middleware


async def user_agent_middleware(app, handler):
    async def middleware(request):
        headers = request.headers
        request.user_agent = headers.get('User-Agent', '')
        response = await handler(request)
        return response

    return middleware


def setup_middlewares(app):
    error_middleware = error_pages({404: handle_404,
                                    405: handle_405,
                                    500: handle_500})
    app.middlewares.append(error_middleware)
    app.middlewares.append(ip_middleware)
    app.middlewares.append(cookie_middleware)
    app.middlewares.append(referer_middleware)
    app.middlewares.append(user_agent_middleware)
