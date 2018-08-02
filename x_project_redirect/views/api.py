__all__ = ['click', 'validate', 'filtered', 'redirect']

from aiohttp.web import HTTPFound

from x_project_redirect.processing import Processing
from x_project_redirect.headers import *
from x_project_redirect.logger import logger, exception_message


@cache()
@cookie()
@csp()
@not_robot()
async def click(request):
    res = HTTPFound('https://yottos.com')
    try:
        processing = Processing(request)
        res = await processing.click()
    except Exception as ex:
        logger.error(exception_message(exc=str(ex), request=str(request.message)))
    return res


@cache()
@cookie()
@csp()
@not_robot()
async def validate(request):
    res = HTTPFound('https://yottos.com')
    try:
        processing = Processing(request)
        res = await processing.validate()
    except Exception as ex:
        logger.error(exception_message(exc=str(ex), request=str(request.message)))
    return res


@cache()
@cookie()
@csp()
@not_robot()
async def filtered(request):
    res = HTTPFound('https://yottos.com')
    try:
        processing = Processing(request)
        res = await processing.filtered()
    except Exception as ex:
        logger.error(exception_message(exc=str(ex), request=str(request.message)))
    return res


@cache()
@cookie()
@csp()
@not_robot()
async def redirect(request):
    res = HTTPFound('https://yottos.com')
    try:
        processing = Processing(request)
        res = await processing.redirect()
    except Exception as ex:
        logger.error(exception_message(exc=str(ex), request=str(request.message)))
    return res
