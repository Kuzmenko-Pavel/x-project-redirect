from aiohttp.web import HTTPNotImplemented, HTTPFound
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse
import random


class BaseProcessing:
    source = 'base'
    utm_source = 'yottos'
    utm_campaign = 'yottos'
    utm_medium = 'yottos'
    utm_term = 'yottos'
    utm_rand = str(random.randint(0, 1000000))

    def __init__(self, request):
        self.request = request

    async def click(self):
        location = self.request.app.router['validate'].url_for(source=self.source)
        return HTTPFound(location)

    async def validate(self):
        location = self.request.app.router['filtered'].url_for(source=self.source)
        return HTTPFound(location)

    async def filtered(self):
        location = self.request.app.router['redirect'].url_for(source=self.source)
        return HTTPFound(location)

    async def redirect(self):
        return HTTPNotImplemented()

    async def get_utm_source(self, *args, **kwargs):
        return self.utm_source

    async def get_utm_campaign(self, *args, **kwargs):
        return self.utm_campaign

    async def get_utm_medium(self, *args, **kwargs):
        return self.utm_medium

    async def get_utm_term(self, *args, **kwargs):
        return self.utm_term

    async def get_utm_rand(self, *args, **kwargs):
        return self.utm_rand

    async def get_default_utm(self, name):
        return 'yottos_facebook'

    async def __add_makros(self, params, values):
        for key, value in params.items():
            for i in ['{source}', '{source_id}', '{source_guid}',
                      '{campaign}', '{campaign_id}', '{campaign_guid}', '{name}',
                      '{offer}', '{offer_id}', '{offer_guid}', '{rand}']:
                value = value.replace(i, values.get(i, await self.get_default_utm(i)))
            params[key] = value
        return urlencode(params)

    async def __add_dynamic_param(self, url, offer, campaign):
        try:
            values = {
                '{source}': await self.get_utm_source(offer, campaign),
                '{campaign}': await self.get_utm_campaign(offer, campaign)
            }
            url_parts = list(urlparse(url))
            params = dict(parse_qsl(url_parts[3]))
            if len(params) > 0:
                url_parts[3] = await self.__add_makros(params, values)

            query = dict(parse_qsl(url_parts[4]))
            if len(query) > 0:
                url_parts[4] = await self.__add_makros(query, values)
            url = urlunparse(url_parts)
        except Exception as e:
            print(e)
        return url

    async def utm_converter(self, url, offer, campaign):
        return await self.__add_dynamic_param(url, offer, campaign)