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

class DoubanmoviePipeline(object):
    def __init__(self):
        self.dbpool=adbapi.ConnectionPool(
            'MySQLdb',
            db='doubanmovie',
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
        tx.execute("select * from doubanmovie where name= %s",item['name'][0])
        result=tx.fetchone()
        logging.debug(result)
        print(result)
        if result:
            logging.debug("Item already stored in db:%s"% item)
        else:   
            classification=actor=''
            classificationLen=len(item['classification'])
            actorLen=len(item['actor'])
            for x in xrange(classificationLen):
                classification+=item['classification'][x]
                if x<classificationLen-1:
                    classification+='/'
            for x in xrange(actorLen):
                actor+=item['actor'][x]
                if x<actorLen-1:
                    actor+='/'
            tx.execute("insert into doubanmovie (name,year,score,director,classification,actor) values (%s,%s,%s,%s,%s,%s)",\
                       (item['name'][0],item['year'][0],item['score'][0],item['director'][0],classification,actor))
            logging.debug("Item stored in db: %s" % item)
        
