from celery import Celery, signals
import os.path
import sys
import yaml
from pymongo import errors, MongoClient

from trafaret_config.simple import read_and_validate

from x_project_redirect.utils import TRAFARET_CONF

app = None


def standard_argparse_options(argument_parser, default_config):
    argument_parser.add_argument('-y', '--yaml', default=default_config,
        help="Configuration file (default: %(default)r)")
    argument_parser.add_argument('--print-yaml-config', action='store_true',
        help="Print config as it is read after parsing and exit")
    argument_parser.add_argument('-Y', '--check-yaml-config', action='store_true',
        help="Check configuration and exit")


def config_from_options(options, trafaret):
    try:
        yaml_conf = options.get('yaml')
        config = read_and_validate(yaml_conf, trafaret)
    except Exception as e:
        print(e)
        sys.exit(1)

    if options.get('print_yaml_config', False):
        yaml.dump(config, sys.stdout, default_flow_style=False)
        sys.exit(0)

    if options.get('check_yaml_config', False):
        sys.exit(0)

    return config


def load():
    global app
    app = Celery('x_project_redirect.celery_worker')
    app.user_options['preload'].add(add_preload_arguments)
    imp = True
    for x in sys.argv:
        if 'worker' == x:
            imp = False
    if imp:
        get_config()


def get_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    options = {'yaml': dir_path + '/../../conf.yaml'}
    config = config_from_options(options, TRAFARET_CONF)
    init_celery(config)


def add_preload_arguments(parser):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    standard_argparse_options(parser.add_argument_group('configuration'), default_config=dir_path + '/../../conf.yaml')


@signals.user_preload_options.connect
def handle_preload_options(options, app, **kwargs):
    config = config_from_options(options, TRAFARET_CONF)
    init_celery(config)


def get_celery_configuration(config):
    config_dict = {}
    for key, value in config.get('celery', {}).items():
        config_dict[key] = value
    return config_dict


def get_mongo_configuration(config):
    config_dict = {}
    for key, value in config.get('mongo', {}).items():
        config_dict[key] = value
    return config_dict

def mongo_connection(host):
    u"""Возвращает Connection к серверу MongoDB"""
    try:
        connection = MongoClient(host=host, maxPoolSize=20)
    except errors.AutoReconnect:
        from time import sleep
        sleep(1)
        connection = MongoClient(host=host, maxPoolSize=20)
    return connection


def check_collection(config):
    avg_obj_size = 500
    max_obj = 5000000
    collection = {'click': 'log.click'}#config['collection']
    collection_name = [x for x in collection.values()]
    connection = mongo_connection(config['uri'])
    db = connection[config['db']]
    for name in collection_name:
        options = db[name].options()
        if not options.get('capped', False):
            print('Create collection %s' % name)
            db.drop_collection(name)
            db.create_collection(name, size=max_obj * avg_obj_size, capped=True, max=max_obj)
            db[name].create_index('dt', background=True)
            db[name].create_index('ip', background=True)


def init_celery(config):
    global app
    celery_config = get_celery_configuration(config)
    app.config_from_object(celery_config)
    app.mongo_config = get_mongo_configuration(config)
    check_collection(app.mongo_config)


@signals.task_prerun.connect
def prerun_task(task_id, task, *args, **kwargs):
    task.mongo_connection = mongo_connection(task._app.mongo_config['uri'])
    task.db = task.mongo_connection[task._app.mongo_config['db']]
    task.collection_click = task.db[task._app.mongo_config['collection']['click']]
    task.collection_blacklist = task.db[task._app.mongo_config['collection']['blacklist']]


load()


if __name__ == '__main__':
    app.start()
