from aiohttp import web
import base64
import binascii
from datetime import datetime
from .base import BaseProcessing
from x_project_redirect.celery_worker.tasks import add


class FbProcessing(BaseProcessing):
    source = 'fb'
    utm_source = 'yottos_facebook'
    utm_campaign = 'yottos_facebook'

    async def click(self):
        query = self.request.query_string
        location = self.request.app.router['validate'].url_for(source=self.source).with_query(query)
        return web.HTTPFound(location)

    async def validate(self):
        query = self.request.query_string
        location = self.request.app.router['filtered'].url_for(source=self.source).with_query(query)
        return web.HTTPFound(location)

    async def filtered(self):
        query = self.request.query_string
        location = self.request.app.router['redirect'].url_for(source=self.source).with_query(query)
        return web.HTTPFound(location)

    async def redirect(self):
        query = self.request.query_string
        try:
            query_lines = base64.urlsafe_b64decode(query).decode('utf-8')
        except binascii.Error as e:
            print(e)
            query_lines = ''
        params = dict([(x.partition('=')[0], x.partition('=')[2]) for x in query_lines.splitlines()])
        campaign = params.get('camp')
        offer = params.get('id')
        url = params.get('url')
        ip = self.request.referer
        referer = self.request.referer
        user_agent = self.request.user_agent
        cookie = self.request.user_cookie
        click_datetime = datetime.now()
        if campaign and offer and url:
            url = await self.utm_converter(url, offer, campaign)
            try:
                add.delay(url, ip, offer, campaign, click_datetime, referer, user_agent, cookie)
            except Exception as ex:
                print(ex)
                add(url, ip, offer, campaign, click_datetime, referer, user_agent, cookie)
        else:
            url = 'https://yottos.com'
        return web.HTTPFound(url)