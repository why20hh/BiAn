import requests
from time import sleep
import re
from lxml import etree
from selenium.webdriver import Chrome
from requests import cookies
import os


class GetBian:
    def __init__(self):
        self.name = None
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.103 Safari/537.36'
        }
        self.driver = Chrome()
        self.sl_num = 1

    def first(self, url):
        url = url
        self.driver.get(url)
        input('登录后输入任意字符继续！')
        data = self.driver.page_source
        classification = re.findall('<div class="nav cate"><em></em>(.+?)</div></li>', data, re.S)
        if len(classification) == 0:
            print('可能被限制了')

        else:
            end_classification = classification[0]
            print(end_classification)
            get_class = re.findall('>(.+?)</a>', end_classification, re.S)[1:-1]
            get_class_link = re.findall('<a href="(.+?)"', end_classification)[1:-1]
            end_get_class = dict(zip(get_class, get_class_link))
            # print(end_get_class)
            for i in end_get_class.keys():
                print(i)
            self.name = input('请输入需要下载的分类的名称：')
            get_link = end_get_class[self.name]
            # print(f'您选择的序号的链接是：{get_link}')
            end_link = 'http://www.netbian.com' + get_link
            # print(end_link)
            self.second(end_link)

    def get_cookie(self):
        sel_cookies = self.driver.get_cookies()
        jar = requests.cookies.RequestsCookieJar()  # 先构建RequestsCookieJar对象
        for i in sel_cookies:
            jar.set(i['name'], i['value'], domain=i['domain'], path=i['path'])
        self.session = requests.session()
        self.session.cookies.update(jar)

    def second(self, end_link):
        self.get_cookie()
        url = end_link
        res = self.session.get(url).content.decode('gbk')  # 右键检查 head/meta/@charset 为编码格式
        html_str = etree.HTML(res)
        # print(html_str)
        all_titles = html_str.xpath('//*[@id="main"]/div[3]/ul/li/a/b/text()')
        urls = html_str.xpath('//*[@id="main"]/div[3]/ul/li/a/@href')
        next_url = html_str.xpath('//*[@class="prev"]/@href')[-1]
        if len(next_url) == 0:
            print('应该所有图片都爬取完了')
        else:
            next_url = 'http://www.netbian.com' + str(next_url)
            all_urls = ['http://www.netbian.com' + str(i) for i in urls]
            fl_dict = dict(zip(all_titles, all_urls))
            for i in fl_dict.keys():
                self.third(i, fl_dict[i])
        sleep(5)
        self.second(next_url)

    def third(self, i, fl_dicts):
        global photo_sl_dir
        url = fl_dicts
        title = i
        res = self.session.get(url).content.decode('gbk')
        html_str = etree.HTML(res)
        end_url = html_str.xpath('//*[@id="main"]/div[3]/div/p/a/img/@src')[0]  # 得到图片的下载按钮的链接
        # print(end_url)
        img_content = self.session.get(end_url, headers=self.headers).content
        if self.sl_num < 99:
            photo_sl_dir = '1-99'
        elif int(str(self.sl_num)[0]) == 1:
            photo_sl_dir = '100-199'
        elif int(str(self.sl_num)[0]) == 2:
            photo_sl_dir = '200-299'
        if not os.path.exists(r'.\{}\{}'.format(self.name, photo_sl_dir)):  # os模块判断并创建
            os.makedirs(r'.\{}\{}'.format(self.name, photo_sl_dir))
        with open(r'.\{}\{}\{}.jpg'.format(self.name, photo_sl_dir, title), 'wb') as f:
            f.write(img_content)
            f.close()
            print(f'{self.sl_num}.{i}已下载')
        self.sl_num += 1


url = 'http://www.netbian.com/'
a = GetBian()
a.first(url)
