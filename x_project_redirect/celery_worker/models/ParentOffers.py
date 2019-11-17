# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

__author__ = 'kuzmenko-pavel'

from sqlalchemy import Column, String, Integer, BigInteger, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy_utils import force_auto_coercion, force_instant_defaults, ChoiceType, URLType, LtreeType, UUIDType
from facebook_exporter.models.choiceTypes import CurrencyType

from .custom_arrays import ArrayOfCustomType
from facebook_exporter.models.meta import ParentBase

force_auto_coercion()
force_instant_defaults()


class ParentOffer(ParentBase):
    __tablename__ = 'v_facebook_offers'
    id = Column(BigInteger, primary_key=True)
    guid = Column(UUIDType(binary=True))
    id_campaign = Column(BigInteger)
    id_account = Column(BigInteger)
    guid_account = Column(BigInteger)
    guid_campaign = Column(BigInteger)
    title = Column(String)
    description = Column(String)
    url = Column(URLType)
    price = Column(String)
    currency = Column(ChoiceType(CurrencyType, impl=Integer()))
    id_retargeting = Column(Text)
    recommended = Column(ARRAY(BigInteger))
    images = Column(ArrayOfCustomType(URLType))
    categories = Column(ArrayOfCustomType(LtreeType))
