__all__ = ['click', 'validate', 'filtered', 'redirect']
from aiohttp import web
from x_project_redirect.celery_worker.tasks import add
import re
from x_project_redirect.logger import logger, exception_message


async def click(request):
    add.delay(5,6)
    return web.Response(text='Hello Aiohttp!')


async def validate(request):
    return web.Response(text='Hello Aiohttp!')


async def filtered(request):
    return web.Response(text='Hello Aiohttp!')


async def redirect(request):
    return web.Response(text='Hello Aiohttp!')