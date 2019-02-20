import argparse
import uvloop
import asyncio
import os
import sys

from aiohttp import web
import aiohttp_debugtoolbar
from trafaret_config import commandline

from x_project_redirect.templates import init_templates
from x_project_redirect.celery_worker import init_celery
from x_project_redirect.logger import logger, exception_message
from x_project_redirect.middlewares import setup_middlewares
from x_project_redirect.routes import setup_routes
from x_project_redirect.utils import TRAFARET_CONF


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def init(loop, argv):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ap = argparse.ArgumentParser(description='Great Description To Be Here')
    ap.add_argument('-s', "--socket", action='store', dest='socket', help='unix socket')
    commandline.standard_argparse_options(ap.add_argument_group('configuration'),
                                          default_config=dir_path + '/../conf.yaml')

    options = ap.parse_args(argv)
    config = commandline.config_from_options(options, TRAFARET_CONF)
    config['socket'] = options.socket
    app = web.Application(loop=loop)
    app['config'] = config
    if app['config']['debug']['console']:
        aiohttp_debugtoolbar.setup(app)
    init_celery(config)
    init_templates(app)
    setup_routes(app)
    setup_middlewares(app)

    return app


def main(argv):
    loop = asyncio.get_event_loop()
    app = init(loop, argv)
    app['log'] = logger
    if app['config']['socket']:
        os.makedirs(os.path.dirname(app['config']['socket']), exist_ok=True)
        web.run_app(app, path=app['config']['socket'], backlog=1024, access_log=logger)
    else:
        web.run_app(app, host=app['config']['host'], port=app['config']['port'], backlog=1024, access_log=logger)


if __name__ == '__main__':
    main(sys.argv[1:])
