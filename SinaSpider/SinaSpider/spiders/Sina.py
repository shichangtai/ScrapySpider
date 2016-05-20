#-*- coding:utf-8 -*-
#所有的下一页功能需要修改
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider,Rule
from scrapy import Request,FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.shell import inspect_response
from SinaSpider.items import SinaspiderItem
import logging
import requests
import re
#from scrapy.http.cookies import CookieJar
#正则表达式中文范围ur"[\u4e00-\u9fa5]+"
#数据库varchar的上限不足时可能引起重复添加等问题

class SinaSpider(CrawlSpider):
    name='sina'
    allowed_domains=['weibo.cn']
    start_urls=["http://login.weibo.cn/login/"]
    #rules=[]                                        
    def __init__(self,*args,**kwargs):
        super(SinaSpider,self).__init__(*args, **kwargs)  # 这里是关键,不然_rule错误
        self.account='Your_account'
        self.password='Your_password'
        self.baseUrl='http://weibo.cn'
    def parse_start_url(self, response):
        sel=Selector(response)
        passwd=sel.xpath(r'/html/body/div[2]/form/div/input[2]/@name').extract_first()
        captchaUrl=sel.xpath(r'/html/body/div[2]/form/div/img[1]/@src').extract_first()
        code=requests.get(captchaUrl)
        with open('/home/shichangtai/code.gif','wb') as f:
            f.write(code.content)
        captcha=raw_input('请输入验证码： ')
        #此次的meta是第一次请求获取cookie，以后每次的请求都讲传送这个cookie_jar
        return [FormRequest.from_response(response=response,
                    formdata={'mobile':self.account,passwd:self.password,'code':captcha},
                    meta = {'cookiejar':1},#不要设置'dont_merge_cookies'为True
                    callback=self.after_log)]
    def after_log(self,response):
        #登陆后，选择提取哪些信息
        fans=response.xpath(r'/html/body/div[4]/div[2]/a[3]/@href').extract_first()
        fans=self.baseUrl+fans
        yield  Request(fans,meta={'cookiejar':response.meta['cookiejar']},callback=self.pre_fans) 
    def pre_fans(self,response):
        fansList=response.xpath(r'//div[@class="c"]/table/tr/td/a[1]/@href').extract()
        for i in fansList:
            yield Request(i,meta={'cookiejar':response.meta['cookiejar']},callback=self.parse_fans)
        #继续到下一页
        url_next=response.xpath(ur'//div[@id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract_first()        
        logging.debug('继续爬取下一页好友列表')
        if url_next:
            yield Request(self.baseUrl+url_next,meta={'cookiejar':response.meta['cookiejar']},callback=self.pre_fans)        
    def parse_fans(self,response):
        name=response.xpath(r'//span[@class="ctt"]/text()').extract_first()
        name=name.strip()
        if response.meta.has_key('name'):#同一用户的不同页面间传递name
            name=response.meta['name']        
        messageDiv=response.xpath(r'//div[@class="c" and @id]')#针对每条状态
        for x in messageDiv:
            item=SinaspiderItem()
            content=x.xpath(r'div/span[@class="ctt"]//text()').extract()      
            likes=re.findall(ur'\u8d5e\[\d*\]',x.extract())[-1]#区分转发情况原作者的赞和本人的赞
            forwards=re.findall(ur'\u8f6c\u53d1\[\d*\]',x.extract())[-1]
            comments=re.findall(ur'\u8bc4\u8bba\[\d*\]',x.extract())[-1]
            other=x.xpath(r'div/span[@class="ct"]/text()').extract_first()#发送时间和发送设备
            if name:
                item['name']=name
            if content:
                item['content']=''.join(content)
            if likes:
                item['likes']=likes
            if forwards:
                item['forwards']=forwards
            if comments:
                item['comments']=comments
            if other:
                item['other']=other
            yield item
        url_next=response.xpath(ur'//div[@class="pa" and @id="pagelist"]/form/div/a[text()="\u4e0b\u9875"]/@href').extract_first()        
        logging.debug(name)
        logging.debug('继续爬取用户的下一页微博内容')
        if url_next:
            yield Request(self.baseUrl+url_next,meta={'cookiejar':response.meta['cookiejar'],'name':name},callback=self.parse_fans)               

"""
其下为原先练习使用的selenium和phantomjs登陆方法，较scrapy框架而言代码比较冗余
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
cap=webdriver.DesiredCapabilities.PHANTOMJS
cap["phantomjs.page.settings.resourceTimeout"] = 1000
self.driver = webdriver.PhantomJS(desired_capabilities=cap) 
def parse_start_url1(self, response):
        self.driver.get(response.url)
        accountField=self.driver.find_element_by_xpath(r'/html/body/div[2]/form/div/input[1]')
        passwdField=self.driver.find_element_by_xpath(r'/html/body/div[2]/form/div/input[2]')
        captchaField=self.driver.find_element_by_xpath(r'/html/body/div[2]/form/div/input[3]')
        accountField.send_keys('18811409451')
        passwdField.send_keys('8288443')
        codeField=self.driver.find_element_by_xpath(r'/html/body/div[2]/form/div/img[1]')
        captchaUrl=codeField.get_attribute('src')
        code=requests.get(captchaUrl)
        with open('/home/shichangtai/code.gif','wb') as f:
            f.write(code.content)
        captcha=raw_input('请输入验证码： ')
        captchaField.send_keys(captcha)
        logClick=self.driver.find_element_by_xpath(r'/html/body/div[2]/form/div/input[10]')
        logClick.click()
        #登陆成功
        fans=self.driver.find_element_by_xpath(r'/html/body/div[4]/div[2]/a[3]')
        fans.click()
        url=self.driver.find_element_by_xpath(r'//*[@id="pagelist"]/form/div/a').get_attribute('href')
        #及时html里显示相对路径，抓取前缀亦有weibo.cn
        yield  Request(url)         
"""