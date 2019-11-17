# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

__author__ = 'kuzmenko-pavel'

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy_utils import force_auto_coercion, force_instant_defaults, ChoiceType, UUIDType
from facebook_exporter.models.choiceTypes import CampaignPaymentModel

from facebook_exporter.models.meta import ParentBase

force_auto_coercion()
force_instant_defaults()


class ParentCampaign(ParentBase):
    __tablename__ = 'v_facebook_campaigns'
    id = Column(BigInteger, primary_key=True)
    id_account = Column(BigInteger)
    guid = Column(UUIDType(binary=True))
    guid_account = Column(UUIDType(binary=True))
    name = Column(String)
    utm = Column(Boolean)
    utm_human_data = Column(Boolean)
    disable_filter = Column(Boolean)
    time_filter = Column(Integer)
    payment_model = Column(ChoiceType(CampaignPaymentModel, impl=Integer()))
    offer_count = Column(BigInteger)
    geo = Column(ARRAY(BigInteger))
    device = Column(ARRAY(BigInteger))
    cron = Column(JSON)
    click_cost = Column(Float)
    impression_cost = Column(Float)
