#-*- coding:utf-8 -*-
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider,Rule
from scrapy import Request
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from doubanmovie.items import DoubanmovieItem
#正则表达式中文范围ur"[\u4e00-\u9fa5]+"
#数据库varchar的上限不足时可能引起重复添加等问题

class MovieSpider(CrawlSpider):
    name='doubanmovie'
    allowed_domains=['movie.douban.com']
    start_urls=["https://movie.douban.com/top250"]
    rules=[
        Rule(SgmlLinkExtractor(allow=(r'https://movie.douban.com/subject/\d+')),callback="parse_item"),
    ]
    #process_links="add_baseUrl"
    #def add_baseUrl(self,links):#接收到的是一个listLink参数
    def parse_start_url(self, response):
        baseUrl='https://movie.douban.com/top250'
        sel=Selector(response)
        for url in sel.xpath(r'//*[@id="content"]/div/div[1]/div[2]/a/@href').extract():
            yield  Request(baseUrl+url)
               
    def parse_item(self,response):
        sel=Selector(response)
        item=DoubanmovieItem()
        item['name']=sel.xpath('//*[@id="content"]/h1/span[1]/text()').extract()
        item['year']=sel.xpath('//*[@id="content"]/h1/span[2]/text()').re(r'\((\d+)\)')
        item['score']=sel.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()').extract()
        item['director']=sel.xpath('//*[@id="info"]/span[1]/span[2]/a/text()').extract()
        item['classification']= sel.xpath('//span[@property="v:genre"]/text()').extract()
        item['actor']= sel.xpath('//*[@id="info"]/span[3]/span[2]/a/text()').extract()
        return item
    