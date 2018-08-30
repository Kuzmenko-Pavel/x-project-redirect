from datetime import datetime
from .base import BaseProcessing
from x_project_redirect.celery_worker.tasks import add
from x_project_redirect.logger import logger, exception_message


class FbProcessing(BaseProcessing):
    source = 'fb'
    utm_medium = 'cpcf'

    async def click(self):
        query = self.request.query_string
        location = self.request.app.router['validate'].url_for(source=self.source).with_query(query)
        if self.request.bot:
            logger.warning(exception_message(exc='BOT FOUND', request=str(self.request.message)))
            return self.http_found(location)
        return self.http_found(location)

    async def validate(self):
        query = self.request.query_string
        location = self.request.app.router['filtered'].url_for(source=self.source).with_query(query)
        if self.request.bot:
            logger.warning(exception_message(exc='BOT FOUND', request=str(self.request.message)))
            return self.http_header_found(location)
        return self.http_found(location)

    async def filtered(self):
        query = self.request.query_string
        location = self.request.app.router['redirect'].url_for(source=self.source).with_query(query)
        if self.request.bot:
            logger.warning(exception_message(exc='BOT FOUND', request=str(self.request.message)))
            return self.http_js_found(location)
        return self.http_found(location)

    def utm_exist(self, key, params):
        if key == 'utm_medium':
            return False
        return key in params

    async def redirect(self):
        query = self.request.query_string
        query_lines = await self._decode_base64(query)
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
            if not self.request.bot:
                try:
                    add.delay(url, ip, offer, campaign, click_datetime, referer, user_agent, cookie)
                except Exception as ex:
                    logger.error(exception_message(exc=str(ex), request=str(self.request.message)))
                    add(url, ip, offer, campaign, click_datetime, referer, user_agent, cookie)
            else:
                logger.warning(exception_message(exc='BOT SEND TO URL', request=str(self.request.message)))
        else:
            url = 'https://yottos.com'
        return self.http_found(url)