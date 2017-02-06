__author__='SCT'
#-*- coding:utf-8 -*-
from urllib.request import *
import re,os,time
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

class Spider:
    def __init__(self):
        self.dirName='PlantSpider'
        cap=webdriver.DesiredCapabilities.PHANTOMJS
        cap["phantomjs.page.settings.resourceTimeout"] = 1000
        self.driver = webdriver.PhantomJS(desired_capabilities=cap)
    def loadPageContent(self):
        Index=input("请输入要打印的网页页数（每个网页含20张图片）： ")
        name='水仙'        
        for pageIndex in range(int(Index)):
            pageIndex+=1
            url='http://www.plantphoto.cn/ashx/getphotopage.ashx?page='+str(pageIndex)+'&n=2&group=sp&cid=45193'        
            self.driver.get(url)
            basePhotoUrl=self.driver.find_element_by_xpath(r'//pre')       
            soup=BeautifulSoup(basePhotoUrl.text,'lxml')
            allPhoto=soup.find_all('img')
            self.getDetailPage(allPhoto,name,pageIndex) 
    def getDetailPage(self,baseUrl,name,pageIndex):
        dir0='F:/'+self.dirName+'/'+name+str(pageIndex)
        self.mkdir(dir0)
        print("已建立存储目录: %s" % dir0)
        print('共有%d张图片等待下载..'%(len(baseUrl)))
        photoSet=[]
        for x in baseUrl:
            photoSet.append(x['src'])    
        self.saveImage(photoSet,dir0) 
    def mkdir(self,path):
        path=path.strip()
        if os.path.exists(path):
            return False
        else:
            os.makedirs(path)
            return True  
    def saveImage(self,photoSet,photoDir):
        index=0
        opener=build_opener(HTTPHandler)
        opener.addheaders.append(('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3'))
        for items in photoSet:
            opener.addheaders.append(('Referer',items))
            install_opener(opener)
            response=urlopen(items)
            data=response.read()
            f=open(photoDir+'/'+str(index)+'.jpg','wb')
            f.write(data)
            f.close()
            print("图片%d下载成功！"%index)            
            index+=1 
if __name__=='__main__':
    spider=Spider()
    startTime=datetime.datetime.now()
    spider.loadPageContent()
    endTime=datetime.datetime.now()
    print("下载本页植物图片用时%s"%(str(endTime-startTime)))
    
#print(self.driver.page_source)
#滚动进度条
#js="var q=document.documentElement.scrollTop=3000"
#self.driver.execute_script(js)
#time.sleep(5)

#url=input('请输入包含图片的中国植物志网址:\n')
#self.driver.implicitly_wait(10)#wait time