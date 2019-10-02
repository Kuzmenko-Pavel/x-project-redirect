import time
from datetime import datetime

from x_project_redirect.celery_worker.tasks import add_x
from x_project_redirect.logger import logger, exception_message
from .base import BaseProcessing


class RgProcessing(BaseProcessing):
    source = 'rg'

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
        query = self.request.query.get('b', '')
        query_lines = await self._decode_base64(query)
        params = dict([(x.partition('=')[0], x.partition('=')[2]) for x in query_lines.splitlines()])
        dt = datetime.now()
        ip = self.request.ip
        cookie = self.request.user_cookie
        id_block = params.get('bid')
        id_site = params.get('sid')
        id_account_right = params.get('aidr')
        id_offer = params.get('oid')
        id_campaign = params.get('cid')
        id_account_left = params.get('aidl')
        test = bool(int(params.get('t', 0)))
        clicks_cost_right = float(params.get('ccr', 0))
        clicks_cost_left = float(params.get('ccl', 0))
        social = bool(int(params.get('s', 0)))
        token = params.get('to', '')
        url = params.get('u')
        clicks_time = (int(time.time() * 1000) - int(params.get('tr', int(time.time() * 1000)))) / 1000
        valid = True if self.encrypt_decrypt(params.get('ra', ''), ip) == "valid" else False
        referer = self.request.referer
        user_agent = self.request.user_agent
        if not valid:
            self.bad_user = 'token'
        if self.request.bot:
            self.bad_user = 'bt'
            valid = False
        if referer != '' and 'yottos.com' not in referer:
            logger.warning("!!!!!!! FAKE REFERER !!!!!!!!!")
            self.bad_user = 'referer'
            valid = False
        if all([x is not None for x in [id_block, id_site, id_account_right,
                                        id_offer, id_campaign, id_account_left, url]]):
            url = await self.utm_converter(url, id_offer, id_campaign)
            try:
                add_x.delay(id_block, id_site, id_account_right,
                            id_offer, id_campaign, id_account_left,
                            clicks_cost_right, clicks_cost_left,
                            social, token, clicks_time, valid,
                            test, dt, url, ip, referer, user_agent, cookie, self.cid)
            except Exception as ex:
                logger.error(exception_message(exc=str(ex), request=str(self.request.message)))
                add_x(id_block, id_site, id_account_right,
                      id_offer, id_campaign, id_account_left,
                      clicks_cost_right, clicks_cost_left,
                      social, token, clicks_time, valid,
                      test, dt, url, ip, referer, user_agent, cookie, self.cid)
        else:
            url = 'https://yottos.com'
        return self.http_found(url)
