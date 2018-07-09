from aiohttp import web
from .base import BaseProcessing


class RgProcessing(BaseProcessing):
    source = 'rg'

    def click(self):
        return web.Response(text='Hello RG!')

    def validate(self):
        pass

    def filtered(self):
        pass

    def redirect(self):
        pass