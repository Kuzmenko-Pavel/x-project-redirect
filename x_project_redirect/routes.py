from .views import ApiView


def setup_routes(app):
    app.router.add_route('GET', '/track.fcgi', ApiView)
    app.router.add_route('POST', '/track.fcgi', ApiView)
