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


class ParentBlock(ParentBase):
    __tablename__ = 'v_facebook_blocks'
    id = Column(BigInteger, primary_key=True)
    guid = Column(UUIDType(binary=True))
    id_account = Column(BigInteger)
    id_site = Column(BigInteger)
    site_name = Column(String)
    click_cost_min = Column(Float)
    click_cost_proportion = Column(Integer)
    click_cost_max = Column(Float)
    impression_cost_min = Column(Float)
    impression_cost_proportion = Column(Integer)
    impression_cost_max = Column(Float)
    cost_percent = Column(Integer)
    disable_filter = Column(Boolean)
    time_filter = Column(Integer)
