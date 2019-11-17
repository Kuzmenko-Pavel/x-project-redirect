# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

import socket
from os import environ, getpid

from sqlalchemy import engine_from_config

from .ParentBlocks import ParentBlock
from .ParentCampaigns import ParentCampaign
from .ParentOffers import ParentOffer
from .meta import metadata, DBScopedSession

server_name = socket.gethostname()


def get_engine(settings, prefix='main.sqlalchemy.', **kwargs):
    if 'connect_args' not in kwargs.keys():
        application_name = 'WebClick %s on %s pid=%s' % (environ.get('project', ''), server_name, getpid())
        kwargs['connect_args'] = {"application_name": application_name}
    return engine_from_config(settings, prefix, echo=False, **kwargs)
