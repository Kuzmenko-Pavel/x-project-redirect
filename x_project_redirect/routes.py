from .views import *


def setup_routes(app):
    app.router.add_route('GET', '/click/{source}', click, name='click')
    app.router.add_route('GET', '/click/validate/{source}', validate, name='validate')
    app.router.add_route('GET', '/click/filtered/{source}', filtered, name='filtered')
    app.router.add_route('GET', '/click/redirect/{source}', redirect, name='redirect')
