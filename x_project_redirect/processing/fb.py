from aiohttp import web
from .base import BaseProcessing


class FbProcessing(BaseProcessing):
    source = 'fb'

    def click(self):
        location = self.request.app.router['validate'].url_for(source=self.source)
        return web.HTTPFound(location)

    def validate(self):
        location = self.request.app.router['filtered'].url_for(source=self.source)
        return web.HTTPFound(location)

    def filtered(self):
        location = self.request.app.router['redirect'].url_for(source=self.source)
        return web.HTTPFound(location)

    def redirect(self):
        return web.Response(text='Hello FB!')