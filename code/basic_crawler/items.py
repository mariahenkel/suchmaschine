# -*- coding: utf-8 -*-
from scrapy import Item, Field


class Website(Item):

    """ Simple datastructure for parsed websites.
    We save title, link and the hole html-body."""

    title = Field()
    link = Field()
    body = Field()
