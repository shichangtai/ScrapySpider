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

class DoubanPipeline(object):
    def __init__(self):
        self.dbpool=adbapi.ConnectionPool(
            'MySQLdb',
            db='douban',
            user='root',
            passwd='shi',
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True
        )

    def process_item(self, item, spider):
        if item.get('rank'):
            query=self.dbpool.runInteraction(self.conditional_insert, item)
            query.addErrback(self.handle_error)
            return item
        else:
            query=self.dbpool.runInteraction(self.conditional_insert_review, item)
            query.addErrback(self.handle_error)
            return item

    def handle_error(self,e):
        logging.error(e)

    def conditional_insert(self,tx,item):
        #the second parameter in execute must be iterable!
        tx.execute("select * from top250 where rank = %s", [item['rank']])
        result=tx.fetchone()
        if result:
            #logging.debug(result)
            logging.debug("Item already stored in db:%s" % item)
        else:
            tx.execute("insert into top250 (name,year,score,director,script,classification,actor,story,rank) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                       (item['name'], item['year'], item['score'], item['director'],
                        item['script'], item['classification'], item['actor'], item['story'], item['rank']))
            logging.debug("Item stored in db: %s" % item)

    def conditional_insert_review(self,tx,item):
        #防止重复添加机制有待提高。。。
        tx.execute("select * from reviews where title = %s and user = %s", [item['title'],item['user']])
        result=tx.fetchone()
        if result:
            #logging.debug(result)
            logging.debug("Item already stored in db:%s" % item)
        else:
            tx.execute("insert into reviews (title,user,score,time,content) values (%s,%s,%s,%s,%s)",
                       (item['title'], item['user'], item['score'], item['time'], item['content']))
            logging.debug("Item stored in db: %s" % item)
