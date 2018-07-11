# -*- coding: utf-8 -*-
import re
import requests
from pyquery import PyQuery as pq
import sys,json

headers ={
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'antipas=9234380P159903B1y453G0p598d;',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}


class GuaZiCrawler():

    def __init__(self):
        self.baseurl = 'https://www.guazi.com'
        self.sess = requests.Session()
        self.sess.headers = headers
        self.start_url = 'https://www.guazi.com/bj/buy/'


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
            'gearbox': content('ul[@class="assort clearfix"] li[@class="two"] span').text(),
            'price': content('span[@class="pricestype"]').text(),
        }

        return data_dict


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