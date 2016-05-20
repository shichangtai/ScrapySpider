# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from twisted.enterprise import adbapi
from scrapy.http import Request
import MySQLdb
import MySQLdb.cursors

class SinaspiderPipeline(object):
    def __init__(self):
        self.dbpool=adbapi.ConnectionPool(
            'MySQLdb',
            db='SinaData',
            user='root',
            passwd='Your_password',
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True
        )    
    def process_item(self, item, spider):
        query=self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item
    def handle_error(self,e):
        logging.error(e)
    def _conditional_insert(self,tx,item):
        tx.execute("insert into BlogData (name,content,likes,forwards,comments,other) values (%s,%s,%s,%s,%s,%s)",\
                   (item['name'],item['content'],item['likes'],item['forwards'],item['comments'],item['other']))
        logging.debug("Item stored in db: %s" % item)    
