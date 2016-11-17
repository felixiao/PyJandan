# -*- coding: utf-8-*-
import sys, requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from progressbar import ProgressBar
global bar
class HtmlParser:
    def __init__(self,url='http://jandan.net/ooxx/'):
        self.session = requests.session()
        self.entry_url = url
        self.latest_page = self.get_latest_page()
        self.datas = []

    def get_latest_page(self):
        html = BeautifulSoup(self.session.get(self.entry_url).content,'html.parser')
        page = html.select('span.current-comment-page')[0].string
        return int(page.lstrip('[').rstrip(']'))

    # def parse(self, parse_count=1):
    #     while parse_count >= 1:
    #         parse_count -= 1
    #         self.parse_page(str(self.latest_page-parse_count))

    def parse(self, count=1, range=None):
        global bar
        if range is not None:
            self.latest_page = range[1]
            count = range[1] - range[0]
        elif count <= 0:
            count = self.latest_page
        bar = ProgressBar(total=count)
        pages = []
        while count >= 1:
            count -= 1
            pages.append(str(self.latest_page-count))
            # self.parse_page(str(self.latest_page-count))
        pool = ThreadPool(16)
        pool.map(self.parse_page, pages)
        pool.close()
        pool.join()

    def parse_page(self,page):
        global bar
        User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
        header = {}
        header['User-Agent'] = User_Agent
        proxy = [{'http':'http://183.245.146.39:139'},
                 {'http':'http://182.88.29.70:8123'}]
        try:
            resp = self.session.get(self.entry_url+'page-'+page,timeout=5,headers=header,proxies=proxy).content
        except requests.exceptions.ConnectionError:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('ConnectionError @ '+page)
            return
        except requests.exceptions.ReadTimeout:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('ReadTimeout @ '+page)
            return
        html = BeautifulSoup(resp,'html.parser')
        div_row = html.find_all('div',class_='row')
        div_text = html.find_all('div',class_='text')
        count = len(div_row)
        for i in range(0,count):
            author = div_row[i].select("div.author > strong")[0].string
            time = div_row[i].select("div.author")[0].a.string
            Id = div_text[i].select('span.righttext')[0].a.string
            try:
                oo = 0
                xx = 0
                oo = int(div_text[i].select('div.vote > span')[1].string)
                xx = int(div_text[i].select('div.vote > span')[2].string)
            except Exception:
                sys.stdout.write(' ' * 79 + '\r')
                sys.stdout.write('Error Int @ {0}-{1}'.format(page, Id))

            rate = 0
            if oo+xx > 0:
                rate = int(oo/(oo+xx)*10000)
            rating = 0
            if rate > 9000:
                rating = 5
            elif rate > 7500:
                rating = 4
            elif rate > 5500:
                rating = 3
            elif rate > 2500:
                rating = 2
            elif rate > 500:
                rating = 1
            else:
                rating = 0

            urls = []
            imgs = div_text[i].select('p > img')
            for img in imgs:
                try:
                    if img['src'] is None:
                        continue
                    url = img['src']
                    url = url.replace('/bmiddle/','/large/',1)
                    url = url.replace('/mw600/','/large/',1)
                    url = url.replace('/small/','/large/',1)
                    url = url.replace('/thumbnail/','/large/',1)
                    urls.append(url)
                except KeyError:
                    sys.stdout.write(' ' * 79 + '\r')
                    sys.stdout.write('KeyError : {0} @ {1}-{2}'.format(img, page, Id))
            if len(urls) <= 0:
                continue

            filename = '{0}-{1:0>4}-{2:0>4}-{3}'.format(rate, oo, page,Id)
            num = 0
            for url in urls:
                try:
                    ext = url.split('.')[-1].lower()
                    ext = ext.strip(' ')
                    if ext != 'jpg' and ext !='jpeg' and ext != 'png' and ext != 'gif' and ext != 'bmp' and ext != 'tiff':
                        # sys.stdout.write(' ' * 79 + '\r')
                        # sys.stdout.write('Error ext : {0} @ {1}-{2}'.format(ext, page, Id))
                        ext = 'jpg'
                        # continue
                except Exception:
                    # sys.stdout.write(' ' * 79 + '\r')
                    # sys.stdout.write('Error Img @ {0}-{1}'.format(page,Id))
                    ext = 'jpg'
                    # continue
                if len(urls) > 1:
                    filename = '{0}-{1}.{2}'.format(filename,num,ext)
                else:
                    filename = '{0}.{1}'.format(filename,ext)
                data = {
                    'author':u''+author,
                    'page':page,
                    '_id':Id+'-'+str(num),
                    'oo':oo,
                    'xx':xx,
                    'rate':rate,
                    'rating': rating,
                    'filename':filename,
                    'ext':ext,
                    'url':url
                }
                self.datas.append(data)
                # sys.stdout.write(' ' * 79 + '\r')
                # sys.stdout.write('Added '+data['filename'])
                num += 1
        bar.move()
        bar.log('{0:0>4}'.format(page))

    def get_data(self):
        return self.datas
