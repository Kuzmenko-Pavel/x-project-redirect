__all__ = ['click', 'validate', 'filtered', 'redirect']
from x_project_redirect.processing import Processing


async def click(request):
    processing = Processing(request)
    return await processing.click()


async def validate(request):
    processing = Processing(request)
    return await processing.validate()


async def filtered(request):
    processing = Processing(request)
    return await processing.filtered()


async def redirect(request):
    processing = Processing(request)
    return await processing.redirect()