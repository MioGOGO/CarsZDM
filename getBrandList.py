#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import requests
from pyquery import PyQuery as pq
import sys,json
import datetime,traceback
import threading,MySQLdb
from contextlib import closing
import threading

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


headers ={
'Connection':'keep-alive'
,'Pragma':'no-cache'
,'Cache-Control':'no-cache'
,'Upgrade-Insecure-Requests':'1'
,'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
,'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
,'Referer':'https://www.guazi.com/bj/audi/'
,'Accept-Encoding':'gzip, deflate, br'
,'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'
,'Cookie':'cityDomain=bj; clueSourceCode=10103000312%2300; uuid=4becaa70-0ba1-4056-e131-bdaf7c8fda98; ganji_uuid=2065557042704287505691; sessionid=783eee75-3a35-4656-e5d0-20555fb37027; cainfo=%7B%22ca_s%22%3A%22pz_baidu%22%2C%22ca_n%22%3A%22tbmkbturl%22%2C%22ca_i%22%3A%22-%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_campaign%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22scode%22%3A%2210103000312%22%2C%22ca_transid%22%3Anull%2C%22platform%22%3A%221%22%2C%22version%22%3A1%2C%22client_ab%22%3A%22-%22%2C%22guid%22%3A%224becaa70-0ba1-4056-e131-bdaf7c8fda98%22%2C%22sessionid%22%3A%22783eee75-3a35-4656-e5d0-20555fb37027%22%7D; _gl_tracker=%7B%22ca_source%22%3A%22-%22%2C%22ca_name%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_id%22%3A%22-%22%2C%22ca_s%22%3A%22self%22%2C%22ca_n%22%3A%22-%22%2C%22ca_i%22%3A%22-%22%2C%22sid%22%3A54452930369%7D; antipas=864262ow0838108Cd781dXj0406464; lg=1; close_finance_popup=2018-07-24; preTime=%7B%22last%22%3A1532413441%2C%22this%22%3A1531292845%2C%22pre%22%3A1531292845%7D'
}


class GuaZiCrawler():

    def __init__(self):
        self.baseurl = 'https://www.guazi.com'
        self.sess = requests.Session()
        self.sess.headers = headers
        self.start_url = 'https://www.guazi.com/bj/buy/'
        self.db_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'passwd': 'miaowudi12',
            'db': 'mydb',
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
        sys.exit()
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
        print content
        sys.exit()
        data_dict = {
            'title': content('h2.titlebox').text().strip(),
            'bordingdate': content('ul[@class="assort clearfix"] li[@class="one"] span').text(),
            'km': content('ul[@class="assort clearfix"] li[@class="two"] span').text(),
            'address': content('ul[@class="assort clearfix"]').find('li').eq(2).find('span').text(),
            'displacement': content('ul[@class="assort clearfix"]').find('li').eq(3).find('span').text(),
            'gearbox': content('ul[@class="assort clearfix"] li[@class="two"] span').text(),
            'price': content('span[@class="pricestype"]').text(),
        }

        return data_dict

    def insertBandInfo( self,tupe ):
        sql = ('insert into mydb.BandInfo(PTFrom,EnName,CHName,Url)'
        'values(%s,%s,%s,%s)'
        'on duplicate key update CHName=values(CHName),Url=values(Url)')
        self.execSql( sql,tupe )
    #sys.exit(0)

    def execSql( self,sql,tupe ):
        try:
            conn = MySQLdb.connect(**self.db_config)
            with closing(conn.cursor()) as cursor:
                cursor.executemany(sql, tupe)
                conn.commit()
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def run(self):
        for pageurl in self.page_url(self.start_url):
            for detail_url in self.index_page(pageurl):
                result = self.detail_page(detail_url)
                res = json.dumps( result )
                print(res)
                sys.exit()
            print('*'*200)
            sys.exit()


if __name__ == '__main__':
    gzcrawler = GuaZiCrawler()
    gzcrawler.run()