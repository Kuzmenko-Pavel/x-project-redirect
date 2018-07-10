from datetime import datetime
from dateutil import parser
from uuid import UUID
import pyodbc
from x_project_redirect.celery_worker import app


def mssql_connection_adload():
    conn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=srv-3.yottos.com;DATABASE=Adload;UID=web;PWD=odif8duuisdofj')
    return conn


def add_click(offer_id, campaign_id, click_datetime=None, social=None, cost_percent_click=None):
    try:
        UUID(offer_id)
    except ValueError as ex:
        print(ex)
        return {'ok': False, 'error': 'offer_id should be uuid string! %s' % ex}

    try:
        dt = parser.parse(click_datetime)
    except (ValueError, AttributeError):
        dt = datetime.datetime.now()

    if social is None:
        social = False

    if cost_percent_click is None:
        cost_percent_click = 100
    try:
        connection_adload = mssql_connection_adload()
        click_cost = 0.0

        # Записываем переход
        print("Записываем переход")
        social = int(social)
        try:
            with connection_adload.cursor() as cursor:
                cursor.callproc('ClickAdd', (offer_id, campaign_id, None, dt, social, cost_percent_click))
                for row in cursor:
                    print(row)
                    click_cost = float(row.get('ClickCost', 0.0))
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


@app.task(ignore_result=True)
def add(url, ip, offer, campaign, click_datetime, referer, user_agent, cookie):
    try:
        dt = parser.parse(click_datetime)
    except (ValueError, AttributeError):
        dt = datetime.now()
    print(url, ip, offer, campaign, dt, referer, user_agent, cookie, sep='\n')
    print("Adload request")
    adload_response = add_click(offer, campaign, dt.isoformat())
    adload_ok = adload_response.get('ok', False)
    print("Adload OK - %s" % adload_ok)