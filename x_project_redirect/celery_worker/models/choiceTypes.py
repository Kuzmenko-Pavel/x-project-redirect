# -*- coding: UTF-8 -*-
from __future__ import absolute_import, unicode_literals

__author__ = 'kuzmenko-pavel'
from enum import Enum


class CampaignPaymentModel(Enum):
    ppc = 1
    ppi = 2
    auto = 3


CampaignPaymentModel.ppc.label = 'Pay per click'
CampaignPaymentModel.ppi.label = 'Pay per impression'
CampaignPaymentModel.auto.label = 'Effective PPC & PPI'


class CurrencyType(Enum):
    none = 0
    uah = 1
    usd = 2
    rub = 3
    eur = 3


CurrencyType.none.label = ''
CurrencyType.none.sign = ''
CurrencyType.none.symbol = ''
CurrencyType.usd.label = 'USD'
CurrencyType.usd.sign = 'USD'
CurrencyType.usd.symbol = '$'
CurrencyType.uah.label = 'UAH'
CurrencyType.uah.sign = 'UAH'
CurrencyType.uah.symbol = '₴'
CurrencyType.rub.label = 'RUB'
CurrencyType.rub.sign = 'RUB'
CurrencyType.rub.symbol = '₴'
CurrencyType.eur.label = 'EUR'
CurrencyType.eur.sign = 'EUR'
CurrencyType.eur.symbol = '₴'
