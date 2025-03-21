import base64
import binascii
import random
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse, unquote
from uuid import uuid4

import aiohttp_jinja2
from aiohttp.web import HTTPNotImplemented, HTTPFound

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
    bad_user = None

    makros = ['{source}', '{source_id}', '{source_guid}', '{campaign}', '{campaign_id}', '{campaign_guid}', '{name}',
              '{offer}', '{offer_id}', '{offer_guid}', '{rand}']

    def __init__(self, request):
        self.request = request
        self.cid = str(uuid4())

    async def click(self):
        query = self.request.query_string
        location = self.request.app.router['validate'].url_for(source=self.source).with_query(query)
        return HTTPFound(location)

    async def validate(self):
        query = self.request.query_string
        location = self.request.app.router['filtered'].url_for(source=self.source).with_query(query)
        return HTTPFound(location)

    async def filtered(self):
        query = self.request.query_string
        location = self.request.app.router['redirect'].url_for(source=self.source).with_query(query)
        return HTTPFound(location)

    async def redirect(self):
        return HTTPNotImplemented()

    async def get_utm_source(self, *args, **kwargs):
        return self.utm_source

    async def get_utm_campaign(self, *args, **kwargs):
        return self.utm_campaign

    async def get_utm_medium(self, *args, **kwargs):
        return self.utm_medium

    async def get_utm_content(self, *args, **kwargs):
        return self.utm_medium

    async def get_utm_term(self, *args, **kwargs):
        return self.utm_term

    async def get_utm_rand(self, *args, **kwargs):
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

    async def get_makros_values(self, *args, **kwargs):
        return {
                '{source}': await self.get_utm_source(*args, **kwargs),
                '{campaign}': await self.get_utm_campaign(*args, **kwargs),
                '{medium}': await self.get_utm_medium(*args, **kwargs)
            }

    async def get_utm_keys(self, *args, **kwargs):
        return {
                'utm_medium': await self.get_utm_medium(*args, **kwargs),
                'utm_source': await self.get_utm_source(*args, **kwargs),
                'utm_campaign': await self.get_utm_campaign(*args, **kwargs),
                'utm_content': await self.get_utm_content(*args, **kwargs),
                'utm_term': await self.get_utm_term(*args, **kwargs),
            }

    async def __add_dynamic_param(self, url, *args, **kwargs):
        try:
            values = await self.get_makros_values(*args, **kwargs)
            url_parts = list(urlparse(url))
            params = dict(parse_qsl(url_parts[3]))
            if len(params) > 0:
                url_parts[3] = await self.__add_makros(params, values)

            query = dict(parse_qsl(url_parts[4]))
            if 'yt_cid' not in query:
                query.update({'yt_cid': self.cid})
            if self.bad_user is None:
                query.update({'yt_u_g': 't'})
            else:
                query.update({'yt_u_b': self.bad_user})
            if len(query) > 0:
                url_parts[4] = await self.__add_makros(query, values)
            url = urlunparse(url_parts)
        except Exception as e:
            print(e)
        return url

    async def __add_utm_param(self, url, *args, **kwargs):
        try:
            keys = await self.get_utm_keys(*args, **kwargs)
            url_parts = list(urlparse(url))
            params = dict(parse_qsl(url_parts[3]))
            if len(params) > 0:
                url_parts[3] = await self.__add_utm(params, keys)

            query = dict(parse_qsl(url_parts[4]))
            url_parts[4] = await self.__add_utm(query, keys)
            url = urlunparse(url_parts)
        except Exception as e:
            print(e)
        return url

    async def utm_converter(self, url, *args, **kwargs):
        url = await self.__add_dynamic_param(url, *args, **kwargs)
        return await self.__add_utm_param(url, *args, **kwargs)

    async def _decode_base64(self, data, recursion=None):
        val = ''
        try:

            try:
                data = unquote(unquote(data))
            except Exception as ex:
                logger.error(exception_message(exc=str(ex), request=str(self.request.message)))

            try:
                val = base64.urlsafe_b64decode(data).decode('utf-8')
            except binascii.Error as ex:
                if recursion is None:
                    recursion = 1
                else:
                    recursion += 1
                if str(ex) == 'Incorrect padding' and recursion < 6:
                    missing_padding = len(data) % 4
                    if missing_padding != 0:
                        data += '=' * (4 - missing_padding)
                    val = await self._decode_base64(data, recursion)
                else:
                    logger.error(exception_message(exc=str(ex), request=str(self.request.message)))

        except binascii.Error as ex:
            logger.error(exception_message(exc=str(ex), request=str(self.request.message)))
        return val

    def encrypt_decrypt(self, word, ip):
        key = list(ip)
        output = []

        for i in range(len(word)):
            xor_num = ord(word[i]) ^ ord(key[i % len(key)])
            output.append(chr(xor_num))

        return ''.join(output)

    def http_found(self, url):
        return HTTPFound(url)

    def http_header_found(self, url):
        return aiohttp_jinja2.render_template('header_found.html', self.request,
                                              {'url': url, 'nonce': self.request.nonce})

    def http_js_found(self, url):
        return aiohttp_jinja2.render_template('js_found.html', self.request, {'url': url, 'nonce': self.request.nonce})
