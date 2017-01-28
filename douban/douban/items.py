# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class DoubanItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name=Field()
    year=Field()
    score=Field()
    director=Field()
    script=Field()
    classification=Field()
    actor=Field()
    story=Field()
    rank=Field()

class ReviewItem(Item):
    user=Field()
    score=Field()
    time=Field()
    content=Field()
    title=Field()
