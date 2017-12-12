from .views import *


def setup_routes(app):
    app.router.add_route('GET', '/click', click)
    app.router.add_route('GET', '/click/validate', validate)
    app.router.add_route('GET', '/click/filtered', filtered)
    app.router.add_route('GET', '/click/redirect', redirect)
