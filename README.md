# Scrapy-Spider
Scrapy爬虫，抓取豆瓣影评新浪微博

selenium webdriver + phantomjs 实现登录，验证码的处理方式为自动下载到程序目录后用户手动输入。

反Ban措施： user-agent池交替下载， ip池交替登录， 设置下载延迟与延迟波动 

__douban__:</br>
默认运行为抓取豆瓣电影top250 [排名/名称/年份/评分/导演/编剧/分类/演员/介绍]</br>
scrapy crawl douban -a movie_index=_电影编号_</br>
则运行影评抓取模式 [电影名称/用户/打分/评分时间/评价内容]
![img](https://raw.githubusercontent.com/shichangtai/Scrapy-Spider/master/screenshots/review.png)
![img](https://raw.githubusercontent.com/shichangtai/Scrapy-Spider/master/screenshots/top250.png)

__SinaSpider__:</br>
新浪微博数据 [微博名/微博内容/赞/转发/评论/日期与地点]
![img](https://raw.githubusercontent.com/shichangtai/Scrapy-Spider/master/screenshots/sina.png)

