from datetime import datetime
from dateutil import parser
from uuid import UUID, uuid4
from x_project_redirect.celery_worker.mq import MQ
import pyodbc
from x_project_redirect.celery_worker import app


def mssql_connection_adload():
    return pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=srv-3.yottos.com;DATABASE=Adload;UID=web;PWD=odif8duuisdofj')


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