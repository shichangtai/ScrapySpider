# -*- coding:utf-8 -*-

#scrapy shell -s USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36' https://movie.douban.com/subject/1295644/

from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Spider, Rule
from scrapy import Request, FormRequest
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from bs4 import BeautifulSoup
import re
from douban.items import DoubanItem, ReviewItem
import requests
from selenium import webdriver
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

#正则表达式中文范围ur"[\u4e00-\u9fa5]+"
#数据库varchar的上限不足时可能引起重复添加等问题


class MovieSpider(Spider):

    #scrapy crawl douban -a movie_index=3882715
    def __init__(self, movie_index=None, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        if movie_index:
            self.start_urls = 'https://movie.douban.com/subject/%s/' % movie_index
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.resourceTimeout"] = 300
        self.driver = webdriver.PhantomJS(desired_capabilities=cap)
    name = "douban"
    allowed_domains=['movie.douban.com','www.douban.com','accounts.douban.com']
    #rules=[Rule(SgmlLinkExtractor(allow=(r'https://movie.douban.com/subject/\d+')),callback="parse_item"),]
    #实践证明,不能重定义parse的CrawlSpider+Rules对于有登陆需求的页面来说不太合适
    headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
    "Connection": "keep-alive",
    "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
    #"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    "Referer": "http://www.douban.com/"
    }

    def start_requests(self):
        print 'Preparing login...'
        # xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        # print xsrf
        # FormRequeset.from_response is a function of Scrapy, to post data
        self.driver.get('https://www.douban.com/login')
        captcha_url = BeautifulSoup(self.driver.page_source, 'lxml').find(id='captcha_image')
        if captcha_url:
            captcha_url = captcha_url.get('src')
            code = requests.get(captcha_url)
            with open('/Users/shichangtai/Desktop/douban/code.jpg', 'wb') as f:
                f.write(code.content)
            captcha = raw_input('请输入图中的验证码:')
            captcha_field = self.driver.find_element_by_id("captcha_field")
            captcha_field.send_keys(captcha)
        username = self.driver.find_element_by_id("email")
        password = self.driver.find_element_by_id("password")
        username.send_keys(“******”)
        password.send_keys(“******”)
        self.driver.find_element_by_name("login").click()
        # return [FormRequest.from_response]
        #some pages cannot display without logging in.
        if self.start_urls:
            print self.start_urls
            print '------------Review crawl mode...----------------'
            self.driver.get(self.start_urls)
            review_url=BeautifulSoup(self.driver.page_source,'lxml').find(id='comments-section').find('span',class_='pl').a['href']
            while(1):
                yield Request(review_url, self.parse_review, headers=self.headers, errback=self.errback_review)
                self.driver.get(review_url)
                if BeautifulSoup(self.driver.page_source, 'lxml').find(id='paginator').find_all('a')[-1].get_text()!=u'\u540e\u9875 >':
                    break
                review_url=self.start_urls+'/comments'+BeautifulSoup(self.driver.page_source, 'lxml').find(id='paginator').find_all('a')[-1]['href']
        else:
            print '---------------Top250 crawl mode...---------------'
            for i in range(10):
                temp_url='https://movie.douban.com/top250?start=%s&filter=' % (i*25)
                yield Request(temp_url,self.parse,headers=self.headers)

    def parse_review(self,response):
        movie_title=BeautifulSoup(response.text, 'lxml').find(id='content').h1.get_text().split()[0]
        one_page_reviews=BeautifulSoup(response.text, 'lxml').find(id='comments').find_all('div',class_='comment')
        for item_review in one_page_reviews:
            review_item=ReviewItem()
            review_item['title']=movie_title
            review_item['user']=item_review.find('span',class_='comment-info').a.get_text()
            review_item['score']='' #some people don't mark
            temp=item_review.find('span',class_=re.compile("allstar(10|20|30|40|50) rating"))
            if temp:
                review_item['score']=temp['title']
            review_item['time']=item_review.find('span',class_='comment-time ').get_text().strip()
            review_item['content']=item_review.p.get_text().strip()
            yield review_item

    # process_links="add_baseUrl"
    # def add_baseUrl(self,links):#接收到的是一个listLink参数
    def parse(self,response):
        link_ex = SgmlLinkExtractor(allow=(r'https://movie.douban.com/subject/\d+'))
        for i in link_ex.extract_links(response):
            yield Request(i.url,callback=self.parse_item,headers=self.headers)

    def parse_item(self, response):
        item = DoubanItem()
        temp_html = BeautifulSoup(response.text,'lxml')
        item['rank'] = temp_html.find('span',class_='top250-no').get_text().split('.')[1]
        info = temp_html.find(id='info')
        item['name'] = temp_html.find('h1').find('span').get_text().split()[0]
        item['year'] = re.findall('\d+', temp_html.find('span',class_='year').get_text())[0]
        item['director']=''
        item['script']=''
        item['actor']=''
        role_dict={u'\u5bfc\u6f14':'director',u'\u7f16\u5267':'script',u'\u4e3b\u6f14':'actor'}
        temp=info.find_all('span',class_='pl')
        for items in temp:
            role=role_dict.get(items.get_text())
            if role is not None:
                item[role]=items.find_next('span').get_text()
        item['classification'] = '/'.join([x.get_text() for x in info.find_all('span',property='v:genre')])
        item['score'] = temp_html.find(id='interest_sectl').find('strong',class_='ll rating_num').get_text()
        item['story'] = re.sub('(\s)|(/n)', '', temp_html.find('span',property='v:summary').get_text())
        return item

    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
            self.driver.get(response.url)
            temp_html = BeautifulSoup(self.driver.page_source, 'lxml')
            item = DoubanItem()
            item['rank'] = temp_html.find('span', class_='top250-no').get_text().split('.')[1]
            info = temp_html.find(id='info')
            item['name'] = temp_html.find('h1').find('span').get_text().split()[0]
            item['year'] = re.findall('\d+', temp_html.find('span', class_='year').get_text())[0]
            item['director'] = ''
            item['script'] = ''
            item['actor'] = ''
            role_dict = {u'\u5bfc\u6f14': 'director', u'\u7f16\u5267': 'script', u'\u4e3b\u6f14': 'actor'}
            temp = info.find_all('span', class_='pl')
            for items in temp:
                role = role_dict.get(items.get_text())
                if role is not None:
                    item[role] = items.find_next('span').get_text()
            item['classification'] = '/'.join([x.get_text() for x in info.find_all('span', property='v:genre')])
            item['score'] = temp_html.find(id='interest_sectl').find('strong', class_='ll rating_num').get_text()
            item['story'] = re.sub('(\s)|(/n)', '', temp_html.find('span', property='v:summary').get_text())
            return item

    def errback_review(self, failure):
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
            self.driver.get(response.url)
            temp_html = BeautifulSoup(self.driver.page_source, 'lxml')
            movie_title = temp_html.find(id='content').h1.get_text().split()[0]
            one_page_reviews = temp_html.find(id='comments').find_all('div',class_='comment')
            for item_review in one_page_reviews:
                review_item = ReviewItem()
                review_item['title'] = movie_title
                review_item['user'] = item_review.find('span', class_='comment-info').a.get_text()
                review_item['score'] = ''  # some people don't mark
                temp = item_review.find('span', class_=re.compile("allstar(10|20|30|40|50) rating"))
                if temp:
                    review_item['score'] = temp['title']
                review_item['time'] = item_review.find('span', class_='comment-time ').get_text().strip()
                review_item['content'] = item_review.p.get_text().strip()
                yield review_item

