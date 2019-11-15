#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import requests
from pyquery import PyQuery as pq
import sys,json
import datetime,traceback
import threading
import MySQLdb
from contextlib import closing
import threading

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)



######cookie 的配置可以在 
######chrome的浏览器里面粘贴出来
headers ={
'Connection':'keep-alive'

,'Pragma':'no-cache'

,'Cache-Control':'no-cache'

,'Upgrade-Insecure-Requests':'1'

,'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'

,'Accept':'image/webp,image/apng,image/*,*/*;q=0.8'

,'Referer':'https://www.guazi.com/bj/'

,'Accept-Encoding':'gzip, deflate, br'

,'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'

,'Cookie':'uuid=e8553806-9eb1-428a-ea9b-d60c45041083; cityDomain=bj; clueSourceCode=%2A%2300; user_city_id=12; ganji_uuid=1344519003319341859442; sessionid=fde2ebb4-9102-4287-c0e3-0c350f4b2a08; lg=1; cainfo=%7B%22ca_a%22%3A%22-%22%2C%22ca_b%22%3A%22-%22%2C%22ca_s%22%3A%22self%22%2C%22ca_n%22%3A%22self%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_i%22%3A%22-%22%2C%22scode%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22display_finance_flag%22%3A%22-%22%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%22e8553806-9eb1-428a-ea9b-d60c45041083%22%2C%22ca_city%22%3A%22bj%22%2C%22sessionid%22%3A%22fde2ebb4-9102-4287-c0e3-0c350f4b2a08%22%7D; antipas=1gt27662b27n004990928i0V7; preTime=%7B%22last%22%3A1573729595%2C%22this%22%3A1573718415%2C%22pre%22%3A1573718415%7D'
}


class GuaZiCrawler():

    def __init__(self):
        ##地址
        self.baseurl = 'https://www.guazi.com'
        ##初始化 session
        self.sess = requests.Session()
        self.sess.headers = headers
        ##开始地址
        self.start_url = 'https://www.guazi.com/bj/buy/'
        ###数据库配置
        ###
        self.db_config = {
            ##数据库地址
            'host': '127.0.0.1',
            ##端口号
            'port': 3306,
            ##用户名
            'user': 'root',
            ##密码
            'passwd': 'miaowudi12',
            ##数据库
            'db': 'mydb',
            ##字符集
            'charset': 'utf8'
            }


    def get_page(self, url):
        '''
        下载页面
        :param url: 
        :return: 
        '''
        return pq(self.sess.get(url).text)

    def page_url(self, start_url):
        '''
        获取翻页链接
        :param start_url: 
        :return: 
        '''
        content = self.get_page(start_url)
        listBank = []
        ## 循环得到列表
        for each in content('div[@class="dd-all clearfix js-brand js-option-hid-info"] > ul > li > p > a').items() :
            tmp = []
            url = each.attr.href
            enName = url.split("/")[2]
            con = each.text().encode('utf-8')
            tmp.append('guazi')
            tmp.append( enName )
            tmp.append( con )
            tmp.append( url )
            listBank.append(tmp)
        self.insertBandInfo( listBank )
        ##parse
        page_num_max = max([int(each.text()) for each in content('ul[@class="pageLink clearfix"]  > li > a').items() if re.match(r'\d+', each.text())])

        page_url_list = []
        for i in range(1,page_num_max+1,1):

            base_url = 'https://www.guazi.com/qd/buy/o{}/#bread'.format(i)

            page_url_list.append(base_url)

        return page_url_list

    def index_page(self, start_url):
        '''
        抓取详情页链接
        :param start_url: 
        :return: 
        '''
        content = self.get_page(start_url)
        for each in content('ul[@class="carlist clearfix js-top"]  > li > a').items():

            url = each.attr.href

            if not url.startswith('http'):

                url = self.baseurl + url

                yield url

    def detail_page(self, detail_url):
        '''
        抓取详情信息
        :param detail_url: 
        :return: 
        '''
        content = self.get_page(detail_url)
        data_dict = {
            'title': content('h2.titlebox').text().strip(),

            'bordingdate': content('ul[@class="assort clearfix"] li[@class="one"] span').text(),

            'km': content('ul[@class="assort clearfix"] li[@class="two"] span').text(),

            'address': content('ul[@class="assort clearfix"]').find('li').eq(2).find('span').text(),

            'displacement': content('ul[@class="assort clearfix"]').find('li').eq(3).find('span').text(),

            'gearbox': content('ul[@class="assort clearfix"] li[@class="last"] span').text(),

            'price': content('span[@class="pricestype"]').text(),

            'info':content('div[@class="test-con"]').text(),

        }

        return data_dict


    def insertBandInfo( self,tupe ):
        '''
        写入品牌的方法
        :param tupe: 
        :return: 
        '''
        sql = ('insert into mydb.BandInfo(PTFrom,EnName,CHName,Url)'
        'values(%s,%s,%s,%s)'
        'on duplicate key update CHName=values(CHName),Url=values(Url)')
        self.execSql( sql,tupe )

    
    def insertCarsInfo(self,toAdd):
        '''
        写入明细信息的方法
        :param tupe: 
        :return: 
        '''
        sql = ('insert into mydb.CarsInfo(bordingdate,title,'
            'price,displacement,km,address,gearbox,info)'
        'values(%s,%s,%s,%s,%s,%s,%s,%s)')
        self.execSql( sql,toAdd )




    def execSql( self,sql,tupe ):
        '''
        执行sql 的方法
        :param tupe,sql: 
        :return: 
        '''
        try:
            conn = MySQLdb.connect(**self.db_config)
            with closing(conn.cursor()) as cursor:
                cursor.executemany(sql, tupe)
                conn.commit()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])



    def etlData (self,strdata):
        '''
        去除数据中的中文
        :param strdata: 
        :return: 
        '''
        if strdata and strdata != "":
            strdata = strdata.replace("¥","")
            strdata = strdata.replace("万","")
            strdata = strdata.strip()
            return float(strdata)*10000


    def run(self):
        '''
        run 方法
        :param strdata: 
        :return: 
        '''
        i = 0
        for pageurl in self.page_url(self.start_url):
            toAdd = []
            
            for detail_url in self.index_page(pageurl):
                i = i + 1
                res = self.detail_page(detail_url)
                # res = json.dumps( result )
                
                tmpAdd = []
                tmpAdd.append(res["bordingdate"])

                tmpAdd.append(res["title"])
                ## 价格需要单独处理一次
                tmpAdd.append(self.etlData(res["price"]))

                tmpAdd.append(res["displacement"])

                tmpAdd.append(res["km"])

                tmpAdd.append(res["address"])

                tmpAdd.append(res["gearbox"])

                tmpAdd.append(res["info"])
                toAdd.append(tmpAdd)
                # print i

            self.insertCarsInfo( toAdd )
            if i > 1000 :
                break
        print('*'*200)
        sys.exit()


if __name__ == '__main__':
    gzcrawler = GuaZiCrawler()

    gzcrawler.run()



