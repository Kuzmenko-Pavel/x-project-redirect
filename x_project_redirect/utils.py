import linecache
import sys

import trafaret as T

primitive_ip_regexp = r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'

TRAFARET_CONF = T.Dict({
    T.Key('host'): T.Regexp(primitive_ip_regexp),
    T.Key('port'): T.Int(),
    T.Key('celery'): T.Any(),
    T.Key('mongo'):
        T.Dict({
            'uri': T.String(),
            'db': T.String(),
            T.Key('collection'):
                T.Dict({
                    'click': T.String(),
                    'blacklist': T.String(),
                    'impression': T.String(),
                })
        }),
    T.Key('sqlalchemy'):
        T.Dict({
            'url': T.String(),
            'client_encoding': T.String(),
            'pool_reset_on_return': T.String(),
            'pool_size': T.Int(),
            'max_overflow': T.Int(),
            'echo_pool': T.Bool(),
            'echo': T.Bool(),
            'pool_pre_ping': T.Bool(),
            'pool_recycle': T.Int(),
            'pool_use_lifo': T.Bool()
        }),
    T.Key('debug'): T.Dict({
        T.Key('status', default=False): T.Bool(),
        T.Key('console', default=False): T.Bool(),
    }),
})


def exception_message():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


def encryptDecrypt(input, ip):
    key = list(ip)
    output = []

    for i in range(len(input)):
        xor_num = ord(input[i]) ^ ord(key[i % len(key)])
        output.append(chr(xor_num))

    return ''.join(output)
