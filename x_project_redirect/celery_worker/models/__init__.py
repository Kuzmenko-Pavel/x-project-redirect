# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals


from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import register

from .ParentCampaigns import ParentCampaign
from .ParentOffers import ParentOffer
from .ParentBlocks import ParentBlock
from .meta import metadata, DBScopedSession


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix, echo=False)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    dbsession = session_factory()
    register(dbsession, transaction_manager=transaction_manager)
    return dbsession
