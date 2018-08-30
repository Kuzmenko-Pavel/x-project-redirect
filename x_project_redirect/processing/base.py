from aiohttp.web import HTTPNotImplemented, HTTPFound
import aiohttp_jinja2
import base64
import binascii
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse, unquote
import random

from x_project_redirect.logger import logger, exception_message


class BaseProcessing:
    source = 'base'
    utm_default = 'yottos'
    utm_source = 'yottos'
    utm_campaign = 'yottos'
    utm_content = 'yottos'
    utm_medium = 'yottos'
    utm_term = 'yottos'
    utm_rand = str(random.randint(0, 1000000))

    makros = ['{source}', '{source_id}', '{source_guid}', '{campaign}', '{campaign_id}', '{campaign_guid}', '{name}',
              '{offer}', '{offer_id}', '{offer_guid}', '{rand}']

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

    async def get_utm_source(self, offer, campaign, *args, **kwargs):
        return self.utm_source

    async def get_utm_campaign(self, offer, campaign, *args, **kwargs):
        return self.utm_campaign

    async def get_utm_medium(self, offer, campaign, *args, **kwargs):
        return self.utm_medium

    async def get_utm_term(self, offer, campaign, *args, **kwargs):
        return self.utm_term

    async def get_utm_rand(self, offer, campaign, *args, **kwargs):
        return self.utm_rand

    async def get_default_utm(self, name):
        return self.utm_default

    async def __add_makros(self, params, values):
        for key, value in params.items():
            for i in self.makros:
                value = value.replace(i, values.get(i, await self.get_default_utm(i)))
            params[key] = value
        return urlencode(params)

    def utm_exist(self, key, params):
        return key in params

    async def __add_utm(self, params, keys):
        for key, value in keys.items():
            if not self.utm_exist(key, params):
                params[key] = value
        return urlencode(params)

    async def get_makros_values(self, offer, campaign):
        return {
                '{source}': await self.get_utm_source(offer, campaign),
                '{campaign}': await self.get_utm_campaign(offer, campaign),
                '{medium}': await self.get_utm_medium(offer, campaign)
            }

    async def get_utm_keys(self, offer, campaign):
        return {
                'utm_medium': await self.get_utm_medium(offer, campaign),
                'utm_source': await self.get_utm_source(offer, campaign),
                'utm_campaign': await self.get_utm_campaign(offer, campaign),
                'utm_content': await self.get_utm_medium(offer, campaign),
                'utm_term': await self.get_utm_term(offer, campaign),
            }

    async def __add_dynamic_param(self, url, offer, campaign):
        try:
            values = await self.get_makros_values(offer, campaign)
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

    async def __add_utm_param(self, url, offer, campaign):
        try:
            keys = await self.get_utm_keys(offer, campaign)
            url_parts = list(urlparse(url))
            params = dict(parse_qsl(url_parts[3]))
            if len(params) > 0:
                url_parts[3] = await self.__add_utm(params, keys)

            query = dict(parse_qsl(url_parts[4]))
            if len(query) > 0:
                url_parts[4] = await self.__add_utm(query, keys)
            url = urlunparse(url_parts)
        except Exception as e:
            print(e)
        return url

    async def utm_converter(self, url, offer, campaign):
        url = await self.__add_dynamic_param(url, offer, campaign)
        return await self.__add_utm_param(url, offer, campaign)

    async def _decode_base64(self, data):
        val = ''
        try:

            try:
                data = unquote(unquote(data))
            except Exception as ex:
                logger.error(exception_message(exc=str(ex), request=str(self.request.message)))

            try:
                val = base64.urlsafe_b64decode(data).decode('utf-8')
            except binascii.Error as ex:
                if str(ex) == 'Incorrect padding':
                    missing_padding = len(data) % 4
                    if missing_padding != 0:
                        data += '=' * (4 - missing_padding)
                    val = await self._decode_base64(data)
                else:
                    logger.error(exception_message(exc=str(ex), request=str(self.request.message)))

        except binascii.Error as ex:
            logger.error(exception_message(exc=str(ex), request=str(self.request.message)))
        return val

    def http_found(self, url):
        return HTTPFound(url)

    def http_header_found(self, url):
        return aiohttp_jinja2.render_template('header_found.html', self.request, {'url': url})

    def http_js_found(self, url):
        return aiohttp_jinja2.render_template('js_found.html', self.request, {'url': url, 'nonce': self.request.nonce})
