from aiohttp.web import HTTPNotImplemented, HTTPFound


class BaseProcessing:
    source = 'base'

    def __init__(self, request):
        self.request = request

    def click(self):
        location = self.request.app.router['validate'].url_for(source=self.source)
        return HTTPFound(location)

    def validate(self):
        location = self.request.app.router['filtered'].url_for(source=self.source)
        return HTTPFound(location)

    def filtered(self):
        location = self.request.app.router['redirect'].url_for(source=self.source)
        return HTTPFound(location)

    def redirect(self):
        return HTTPNotImplemented()