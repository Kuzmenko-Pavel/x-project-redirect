from datetime import datetime, timedelta

from dateutil import parser

from x_project_redirect.celery_worker import app
from x_project_redirect.celery_worker.models import ParentBlock, ParentCampaign
from x_project_redirect.celery_worker.models.choiceTypes import CampaignPaymentModel


def blacklist_exist(blacklist, ip, cookie=None):
    border_cookie_count = 1
    border_ip_count = 3
    if cookie is None:
        cookie = 'FACEBOOK'
        border_cookie_count = 5
        border_ip_count = 15

    cookie_count = blacklist.find({'ip': ip, 'cookie': cookie}).count()
    print('Check blacklist by cookie %s' % cookie_count)
    if cookie_count >= border_cookie_count:
        blacklist.update_many({'ip': ip, 'cookie': cookie}, {'$set': {'dt': datetime.now()}}, upsert=True)
        return True
    ip_count = blacklist.find({'ip': ip}).count()
    print('Check blacklist by ip %s' % ip_count)
    if ip_count > border_ip_count:
        return True
    return False


def check_filter(clicks, blacklist, ip, id_block, id_offer, dt, cookie=None):
    # Ищем, не было ли кликов по этому товару
    # Заодно проверяем ограничение на max_clicks_for_one_day переходов в сутки
    # (защита от накруток)

    max_clicks_for_one_day = 3
    max_clicks_for_one_day_all = 5
    max_clicks_for_one_week = 10
    max_clicks_for_one_week_all = 15
    ip_max_clicks_for_one_day = 6
    ip_max_clicks_for_one_day_all = 10
    ip_max_clicks_for_one_week = 20
    ip_max_clicks_for_one_week_all = 30

    if cookie is None:
        cookie = 'FACEBOOK'
        max_clicks_for_one_day = 30
        max_clicks_for_one_day_all = 50
        max_clicks_for_one_week = 100
        max_clicks_for_one_week_all = 150
        ip_max_clicks_for_one_day = 60
        ip_max_clicks_for_one_day_all = 100
        ip_max_clicks_for_one_week = 200
        ip_max_clicks_for_one_week_all = 300

    # Проверяе по рекламному блоку за день и неделю
    today_clicks = 0
    toweek_clicks = 0

    # Проверяе по ПС за день и неделю
    today_clicks_all = 0
    toweek_clicks_all = 0

    # Проверяе по рекламному блоку за день и неделю по ip
    ip_today_clicks = 0
    ip_toweek_clicks = 0

    # Проверяе по ПС за день и неделю по ip
    ip_today_clicks_all = 0
    ip_toweek_clicks_all = 0

    unique = True

    cursor = clicks.find({
        'ip': ip,
        'id_block': id_block,
        'dt': {'$lte': dt, '$gte': (dt - timedelta(weeks=1))}
    }).limit(ip_max_clicks_for_one_day_all + ip_max_clicks_for_one_week_all)

    for click in cursor:
        if click.get('id_block') == id_block:
            if click.get('cookie') == cookie:
                if (dt - click['dt']).days == 0:
                    today_clicks += 1
                    toweek_clicks += 1
                else:
                    toweek_clicks += 1

                if click['id_offer'] == id_offer:
                    unique = False
            else:
                if (dt - click['dt']).days == 0:
                    ip_today_clicks += 1
                    ip_toweek_clicks += 1
                else:
                    ip_toweek_clicks += 1
        else:
            if click.get('cookie') == cookie:
                if (dt - click['dt']).days == 0:
                    today_clicks_all += 1
                    toweek_clicks_all += 1
                else:
                    toweek_clicks_all += 1

                if click['id_offer'] == id_offer:
                    unique = False
            else:
                if (dt - click['dt']).days == 0:
                    ip_today_clicks_all += 1
                    ip_toweek_clicks_all += 1
                else:
                    ip_toweek_clicks_all += 1

    print("Total clicks for day in informers = %s" % today_clicks)
    if today_clicks >= max_clicks_for_one_day:
        print(u'Более %d переходов с РБ за сутки' % max_clicks_for_one_day)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    print("Total clicks for week in informers = %s" % toweek_clicks)
    if toweek_clicks >= max_clicks_for_one_week:
        print(u'Более %d переходов с РБ за неделю' % max_clicks_for_one_week)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    print("Total clicks for day in all partners = %s" % today_clicks_all)
    if today_clicks_all >= max_clicks_for_one_day_all:
        print(u'Более %d переходов с ПС за сутки' % max_clicks_for_one_day_all)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    print("Total clicks for week in all partners = %s" % toweek_clicks_all)
    if toweek_clicks_all >= max_clicks_for_one_week_all:
        print(u'Более %d переходов с ПС за неделю' % max_clicks_for_one_week_all)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    print("Total clicks for day in informers by ip = %s" % today_clicks)
    if ip_today_clicks >= ip_max_clicks_for_one_day:
        print(u'Более %d переходов с РБ за сутки по ip' % ip_max_clicks_for_one_day)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    print("Total clicks for week in informers by ip = %s" % toweek_clicks)
    if ip_toweek_clicks >= ip_max_clicks_for_one_week:
        print(u'Более %d переходов с РБ за неделю по ip' % ip_max_clicks_for_one_week)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    print("Total clicks for day in all partners by ip = %s" % today_clicks_all)
    if ip_today_clicks_all >= ip_max_clicks_for_one_day_all:
        print(u'Более %d переходов с ПС за сутки по ip' % ip_max_clicks_for_one_day_all)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    print("Total clicks for week in all partners by ip = %s" % toweek_clicks_all)
    if ip_toweek_clicks_all >= ip_max_clicks_for_one_week_all:
        print(u'Более %d переходов с ПС за неделю по ip' % ip_max_clicks_for_one_week_all)
        unique = False
        blacklist.update_one({'ip': ip, 'cookie': cookie},
                             {'$set': {'dt': datetime.now()}},
                             upsert=True)

    return unique


def click_cost_calc(block, campaign):
    if campaign.payment_model in [CampaignPaymentModel.ppc, CampaignPaymentModel.auto]:
        cost_percent = block.cost_percent
        cost_proportion = block.click_cost_proportion
        cost_min = block.click_cost_min
        cost_max = block.click_cost_max
        ccl = campaign.click_cost
        ccl = round(ccl * cost_percent / 100, 4)
        ccr = round(ccl * cost_proportion / 100, 4)
        if cost_min and ccr < cost_min:
            ccr = cost_min
        if cost_max and ccr > cost_max:
            ccr = cost_max
        return ccr, ccl
    return 0, 0


@app.task(ignore_result=True, bind=True)
def add(self, id_block, id_site, id_account_right,
        id_offer, id_campaign, id_account_left,
        valid, not_filter, time_filter,
        dt, url, ip, referer, user_agent, cookie, cid):
    print('===============Start Facebook Click===============')
    try:
        print("Block ID = %s" % id_block)
    except Exception:
        pass
    try:
        print("Site ID = %s" % id_site)
    except Exception:
        pass
    try:
        print("Getmyad ID = %s" % id_account_right)
    except Exception:
        pass
    try:
        print("Offer ID = %s" % id_offer)
    except Exception:
        pass
    try:
        print("Campaign ID = %s" % id_campaign)
    except Exception:
        pass
    try:
        print("Adload ID = %s" % id_account_left)
    except Exception:
        pass
    try:
        print("Valid = %s" % valid)
    except Exception:
        pass
    try:
        print("Not Filter = %s" % not_filter)
    except Exception:
        pass
    try:
        print("Time Filter = %s" % time_filter)
    except Exception:
        pass
    try:
        print("Date = %s" % dt)
    except Exception:
        pass
    try:
        print("Url = %s" % url)
    except Exception:
        pass
    try:
        print("IP = %s" % ip)
    except Exception:
        pass
    try:
        print("Referer = %s" % referer)
    except Exception:
        pass
    try:
        print("User Agent = %s" % user_agent)
    except Exception:
        pass
    try:
        print("Cookie = %s" % cookie)
    except Exception:
        pass
    try:
        print("CID = %s" % cid)
    except Exception:
        pass

    unique = True
    suspicious = False
    filtered = False
    banned = False
    try:
        dt = parser.parse(dt)
    except (ValueError, AttributeError, TypeError):
        dt = datetime.now()

    if not not_filter:
        if not valid:
            print("NOT VALID ip:%s" % ip)
            banned = True
            unique = False
        else:
            if blacklist_exist(self.collection_blacklist, ip, cookie):
                print("Blacklisted ip:%s" % ip)
                banned = True
                valid = False
                unique = False

            if valid:
                if referer is None:
                    print('Without Referer ip:%s' % ip)
                    suspicious = True

                if user_agent is None:
                    print('Without User Agent ip:%s' % ip)
                    suspicious = True

                unique = check_filter(self.collection_click, self.collection_blacklist,
                                      ip, id_block, id_offer, dt, cookie)
                print('Unique:%s' % unique)

    clicks_cost_right = 0
    clicks_cost_left = 0
    block = self.dbsession.query(ParentBlock).filter(ParentBlock.id == id_block).one_or_none()
    campaign = self.dbsession.query(ParentCampaign).filter(ParentCampaign.id == id_campaign).one_or_none()
    if block and campaign:
        clicks_cost_right, clicks_cost_left = click_cost_calc(block, campaign)

    try:
        print("Getmyad Click Cost = %s" % clicks_cost_right)
    except Exception:
        pass
    try:
        print("Adload Click Cost = %s" % clicks_cost_left)
    except Exception:
        pass

    if not unique or not valid or banned:
        print('Reset click cost')
        clicks_cost_right = 0
        clicks_cost_left = 0

    click_obj = {
        "id_account_right": id_account_right,
        "id_site": id_site,
        "clicks_cost_right": clicks_cost_right,
        "id_block": id_block,
        "clicks_cost_left": clicks_cost_left,
        "token": '',
        "id_campaign": id_campaign,
        "clicks_time": 60,
        "valid": valid,
        "cookie": cookie,
        "social": False,
        "id_offer": id_offer,
        "dt": dt,
        "ip": ip,
        "id_account_left": id_account_left,
        "referer": referer,
        "user_agent": user_agent,
        "url": url,
        "cid": cid,
        "unique": unique,
        "suspicious": suspicious,
        "filtered": filtered,
        "banned": banned

    }
    self.collection_click.insert_one(click_obj)
    print('===============Stop Facebook Click===============')

    # account_id = get_account(offer, campaign)
    # if account_id:
    #     try:
    #         amqp = MQ()
    #         amqp.click(url=url,
    #                    ip=ip,
    #                    click_datetime=dt.strftime("%Y-%m-%d %H:%M:%S.%f"),
    #                    offer_id=offer,
    #                    campaign_id=campaign,
    #                    informer_id='fb',
    #                    token='',
    #                    referer=referer,
    #                    user_agent=user_agent,
    #                    account_id=account_id,
    #                    adload_cost=adload_cost,
    #                    cid=cid
    #                    )
    #     except Exception as ex:
    #         print(ex)


@app.task(ignore_result=True, bind=True)
def add_x(self, id_block, id_site, id_account_right, id_offer, id_campaign, id_account_left,
          clicks_cost_right, clicks_cost_left, social, token, clicks_time, valid, not_filter, time_filter,
          test, dt, url, ip, referer, user_agent, cookie, cid):
    print('===============Start X Click===============')
    try:
        print("Block ID = %s" % id_block)
    except Exception:
        pass
    try:
        print("Site ID = %s" % id_site)
    except Exception:
        pass
    try:
        print("Getmyad ID = %s" % id_account_right)
    except Exception:
        pass
    try:
        print("Offer ID = %s" % id_offer)
    except Exception:
        pass
    try:
        print("Campaign ID = %s" % id_campaign)
    except Exception:
        pass
    try:
        print("Adload ID = %s" % id_account_left)
    except Exception:
        pass
    try:
        print("Getmyad Click Cost = %s" % clicks_cost_right)
    except Exception:
        pass
    try:
        print("Adload Click Cost = %s" % clicks_cost_left)
    except Exception:
        pass
    try:
        print("Social = %s" % social)
    except Exception:
        pass
    try:
        print("Token = %s" % token)
    except Exception:
        pass
    try:
        print("Click Time = %s" % clicks_time)
    except Exception:
        pass
    try:
        print("Valid = %s" % valid)
    except Exception:
        pass
    try:
        print("Not Filter = %s" % not_filter)
    except Exception:
        pass
    try:
        print("Time Filter = %s" % time_filter)
    except Exception:
        pass
    try:
        print("Test = %s" % test)
    except Exception:
        pass
    try:
        print("Date = %s" % dt)
    except Exception:
        pass
    try:
        print("Url = %s" % url)
    except Exception:
        pass
    try:
        print("IP = %s" % ip)
    except Exception:
        pass
    try:
        print("Referer = %s" % referer)
    except Exception:
        pass
    try:
        print("User Agent = %s" % user_agent)
    except Exception:
        pass
    try:
        print("Cookie = %s" % cookie)
    except Exception:
        pass
    try:
        print("CID = %s" % cid)
    except Exception:
        pass

    unique = True
    suspicious = False
    filtered = False
    banned = False
    try:
        dt = parser.parse(dt)
    except (ValueError, AttributeError, TypeError):
        dt = datetime.now()

    if test:
        print("Processed test click from ip %s" % ip)
        return

    # if ip == '178.165.81.178':
    #     not_filter = True

    if not not_filter:
        if not valid:
            print("NOT VALID ip:%s" % ip)
            banned = True
            unique = False
        else:
            if blacklist_exist(self.collection_blacklist, ip, cookie):
                print("Blacklisted ip:%s" % ip)
                banned = True
                valid = False
                unique = False

            if int(clicks_time) < int(time_filter):
                print("Filtered time by ip:%s" % ip)
                filtered = False
                unique = False
                valid = False

            if valid:
                if referer is None:
                    print('Without Referer ip:%s' % ip)
                    suspicious = True

                if user_agent is None:
                    print('Without User Agent ip:%s' % ip)
                    suspicious = True

                unique = check_filter(self.collection_click, self.collection_blacklist,
                                      ip, id_block, id_offer, dt, cookie)
                print('Unique:%s' % unique)
    if not unique or not valid or banned:
        print('Reset click cost')
        clicks_cost_right = 0
        clicks_cost_left = 0

    click_obj = {
        "id_account_right": id_account_right,
        "id_site": id_site,
        "clicks_cost_right": clicks_cost_right,
        "id_block": id_block,
        "clicks_cost_left": clicks_cost_left,
        "token": token,
        "id_campaign": id_campaign,
        "clicks_time": clicks_time,
        "valid": valid,
        "cookie": cookie,
        "social": social,
        "id_offer": id_offer,
        "dt": dt,
        "ip": ip,
        "id_account_left": id_account_left,
        "referer": referer,
        "user_agent": user_agent,
        "url": url,
        "cid": cid,
        "unique": unique,
        "suspicious": suspicious,
        "filtered": filtered,
        "banned": banned

    }
    self.collection_click.insert_one(click_obj)
    print('===============Stop X Click===============')


@app.task(ignore_result=True, bind=True)
def clean_blacklist(self):
    print(self.collection_blacklist.ip.remove({
        'dt': {'$lte': datetime.now() - timedelta(weeks=2)}
    }))
