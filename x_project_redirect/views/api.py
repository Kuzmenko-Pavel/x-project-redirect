__all__ = ['click', 'validate', 'filtered', 'redirect']
from aiohttp import web
import base64
import re
from x_project_redirect.logger import logger, exception_message, encryptDecrypt
from x_project_redirect.celery_worker.tasks import add


async def click(request):
    add.delay(5,6)
    return web.Response(text='Hello Aiohttp!')


async def validate(request):
    base64_encoded_params = request.query_string
    location = '/click/filtered?%s' % base64_encoded_params
    return web.HTTPFound(location)


async def filtered(request):
    base64_encoded_params = request.query_string
    location = '/click/redirect?%s' % base64_encoded_params
    return web.HTTPFound(location)


async def redirect(request):
    base64_encoded_params = request.query_string
    referer = request.referer
    user_agent = request.user_agent
    cookie = request.user_cookie
    param_lines = base64.urlsafe_b64decode(base64_encoded_params).splitlines()
    params = dict([(x.decode('utf-8').partition('=')[0], x.decode('utf-8').partition('=')[2]) for x in param_lines])
    url = params.get('url', 'https://yottos.com/')
    offer_id = params.get('id', '')
    campaign_id = params.get('camp', '')
    inf_id = params.get('inf', '')
    token = params.get('token', '')
    ip = ''
    valid = True if encryptDecrypt(params.get('rand', ''), ip) == "valid" else False
    print(param_lines)
    print(params)
    return web.Response(text='Hello Aiohttp!\n %s \n %s \n %s \n %s' % (base64_encoded_params,
                                                                        referer,
                                                                        user_agent,
                                                                        cookie))
