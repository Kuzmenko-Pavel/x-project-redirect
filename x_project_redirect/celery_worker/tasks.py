import pyodbc
from datetime import datetime, timedelta
from uuid import UUID

from dateutil import parser

from x_project_redirect.celery_worker import app
from x_project_redirect.celery_worker.mq import MQ


def mssql_connection_adload():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 13 for SQL Server};SERVER=srv-3.yottos.com;DATABASE=Adload;UID=web;PWD=odif8duuisdofj')


def add_click(offer_id, campaign_id, click_datetime=None, social=None, cost_percent_click=None):
    try:
        UUID(offer_id)
    except ValueError as ex:
        print(ex)
        return {'ok': False, 'error': 'offer_id should be uuid string! %s' % ex}
    try:
        UUID(campaign_id)
    except ValueError as ex:
        print(ex)
        return {'ok': False, 'error': 'campaign_id should be uuid string! %s' % ex}

    try:
        dt = parser.parse(click_datetime)
    except (ValueError, AttributeError):
        dt = datetime.datetime.now()

    if social is None:
        social = False

    if cost_percent_click is None:
        cost_percent_click = 100
    try:
        click_cost = 0.0

        # Записываем переход
        print("Записываем переход")
        social = int(social)
        try:
            with mssql_connection_adload() as connection_adload:
                with connection_adload.cursor() as cursor:
                    sql = '''
                    SET NOCOUNT ON;
                    DECLARE @RC int
                    EXECUTE @RC = [Adload].[dbo].[ClickAdd] 
                       '%s'
                      ,'%s'
                      ,null
                      ,null
                      ,0
                      ,100
                    ''' % (offer_id, campaign_id)
                    cursor.execute(sql)
                    click_cost = float(cursor.fetchval())
        except Exception as ex:
            print(ex)
            return {'ok': False, 'error': str(ex)}

        if not social and click_cost == 0.0:
            return {'ok': False, 'error': "adload click cost 0"}
        print("Offer: %s Cost %s" % (offer_id, click_cost))
        return {'ok': True, 'cost': click_cost}

    except Exception as ex:
        print(ex)
        return {'ok': False, 'error': str(ex)}


def get_account(offer_id, campaign_id):
    try:
        UUID(offer_id)
    except ValueError as ex:
        print(ex)
        return {'ok': False, 'error': 'offer_id should be uuid string! %s' % ex}
    try:
        UUID(campaign_id)
    except ValueError as ex:
        print(ex)
        return {'ok': False, 'error': 'campaign_id should be uuid string! %s' % ex}

    account_id = ''
    try:
        with mssql_connection_adload() as connection_adload:
            with connection_adload.cursor() as cursor:
                sql = '''
                SELECT [UserID]
                FROM [Adload].[dbo].[Advertise]
                where [Adload].[dbo].[Advertise].AdvertiseID = '%s'
                ''' % (campaign_id)
                cursor.execute(sql)
                account_id = cursor.fetchval()
    except Exception as ex:
        print(ex)
    print(account_id)
    return account_id


def blacklist_exist(blacklist, ip):
    if blacklist.ip.find_one({'ip': ip}):
        blacklist.ip.update_one({'ip': ip}, {'$set': {'dt': datetime.datetime.now()}}, upsert=True)
        return True
    return False


def check_filter(clicks, blacklist, ip, cookie, block_id, offer_id, dt):
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
        'inf': block_id,
        'dt': {'$lte': dt, '$gte': (dt - timedelta(weeks=1))}
    }).limit(ip_max_clicks_for_one_day_all + ip_max_clicks_for_one_week_all)

    for click in cursor:
        if click.get('inf') == block_id:
            if click.get('cookie') == cookie:
                if (dt - click['dt']).days == 0:
                    today_clicks += 1
                    toweek_clicks += 1
                else:
                    toweek_clicks += 1

                if click['offer'] == offer_id:
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

                if click['offer'] == offer_id:
                    unique = False
            else:
                if (dt - click['dt']).days == 0:
                    ip_today_clicks_all += 1
                    ip_toweek_clicks_all += 1
                else:
                    ip_toweek_clicks_all += 1

    print("Total clicks for day in informers = %s" % today_clicks)
    if today_clicks >= max_clicks_for_one_day:
        error_id = 3
        print(u'Более %d переходов с РБ за сутки' % max_clicks_for_one_day)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    print("Total clicks for week in informers = %s" % toweek_clicks)
    if toweek_clicks >= max_clicks_for_one_week:
        error_id = 4
        print(u'Более %d переходов с РБ за неделю' % max_clicks_for_one_week)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    print("Total clicks for day in all partners = %s" % today_clicks_all)
    if today_clicks_all >= max_clicks_for_one_day_all:
        error_id = 5
        print(u'Более %d переходов с ПС за сутки' % max_clicks_for_one_day_all)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    print("Total clicks for week in all partners = %s" % toweek_clicks_all)
    if toweek_clicks_all >= max_clicks_for_one_week_all:
        error_id = 6
        print(u'Более %d переходов с ПС за неделю' % max_clicks_for_one_week_all)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    print("Total clicks for day in informers by ip = %s" % today_clicks)
    if ip_today_clicks >= ip_max_clicks_for_one_day:
        error_id = 3
        print(u'Более %d переходов с РБ за сутки по ip' % ip_max_clicks_for_one_day)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    print("Total clicks for week in informers by ip = %s" % toweek_clicks)
    if ip_toweek_clicks >= ip_max_clicks_for_one_week:
        error_id = 4
        print(u'Более %d переходов с РБ за неделю по ip' % ip_max_clicks_for_one_week)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    print("Total clicks for day in all partners by ip = %s" % today_clicks_all)
    if ip_today_clicks_all >= ip_max_clicks_for_one_day_all:
        error_id = 5
        print(u'Более %d переходов с ПС за сутки по ip' % ip_max_clicks_for_one_day_all)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    print("Total clicks for week in all partners by ip = %s" % toweek_clicks_all)
    if ip_toweek_clicks_all >= ip_max_clicks_for_one_week_all:
        error_id = 6
        print(u'Более %d переходов с ПС за неделю по ip' % ip_max_clicks_for_one_week_all)
        unique = False
        blacklist.ip.update_one({'ip': ip},
                                {'$set': {'dt': datetime.datetime.now()}},
                                upsert=True)

    return unique


@app.task(ignore_result=True)
def add(url, ip, offer, campaign, click_datetime, referer, user_agent, cookie, cid):
    try:
        dt = parser.parse(click_datetime)
    except (ValueError, AttributeError, TypeError):
        dt = datetime.now()
    print(url, ip, offer, campaign, dt, referer, user_agent, cookie, cid, sep='\n')
    print("Adload request")
    adload_response = add_click(offer, campaign, dt.isoformat())
    adload_ok = adload_response.get('ok', False)
    adload_cost = 0
    if adload_ok:
        adload_cost = adload_response['cost']

    print("Adload OK - %s" % adload_ok)
    account_id = get_account(offer, campaign)
    if account_id:
        try:
            amqp = MQ()
            amqp.click(url=url,
                       ip=ip,
                       click_datetime=dt.strftime("%Y-%m-%d %H:%M:%S.%f"),
                       offer_id=offer,
                       campaign_id=campaign,
                       informer_id='fb',
                       token='',
                       referer=referer,
                       user_agent=user_agent,
                       account_id=account_id,
                       adload_cost=adload_cost,
                       cid=cid
                       )
        except Exception as ex:
            print(ex)


@app.task(ignore_result=True, bind=True)
def add_x(self, id_block, id_site, id_account_right, id_offer, id_campaign, id_account_left,
          clicks_cost_right, clicks_cost_left, social, token, clicks_time, valid, not_filter, time_filter,
          test, dt, url, ip, referer, user_agent, cookie, cid):
    try:
        dt = parser.parse(dt)
    except (ValueError, AttributeError, TypeError):
        dt = datetime.now()

    click_obj = {
        "id_account_right": id_account_right,
        "id_site": id_site,
        "clicks_cost_right": clicks_cost_right,
        "id_block": id_block,
        "clicks_cost_left": clicks_cost_left,
        "token": token,
        "id_campaign": id_campaign,
        "test": test,
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
        "cid": cid
    }
    self.collection_click.insert_one(click_obj)
