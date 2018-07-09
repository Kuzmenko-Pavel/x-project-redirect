__all__ = ['click', 'validate', 'filtered', 'redirect']
from x_project_redirect.processing import Processing


async def click(request):
    processing = Processing(request)
    return processing.click()


async def validate(request):
    processing = Processing(request)
    return processing.validate()


async def filtered(request):
    processing = Processing(request)
    return processing.filtered()


async def redirect(request):
    processing = Processing(request)
    return processing.redirect()