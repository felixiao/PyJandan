# -*- coding: utf-8-*-
import sys, requests, json, os, time
from exif import ExifEditer

class SaveImage:
    def __init__(self, path):
        self.path = path
        self.session = requests.session()
        self.exif = ExifEditer()
        self.path = './ooxx/'
        
    def check_dir(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path,exist_ok=True)

    def save_file(self, data, filename):
        self.check_dir()
        with open(self.path+filename, 'wb') as fp:
            fp.write(data)

    def save_one_data(self, ooxx):
        User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
        header = {}
        header['User-Agent'] = User_Agent
        try:
            data = self.session.get(ooxx['url'],timeout=3,headers=header).content
            self.save_file(data=data,filename=ooxx['filename'])
            if ooxx['ext'] == 'jpg' or ooxx['ext'] == 'jpeg':
                self.exif.write_exif(path=self.path+ooxx['filename'],artist=ooxx['page'],desc=ooxx['_id'],comment=str(ooxx['url']),rating=ooxx['rating'])
            return True
        except requests.exceptions.ReadTimeout:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('ReadTimeout @ '+ooxx['filename'])
            return False
        except requests.exceptions.ConnectionError:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('Connect Err @ '+ooxx['filename'])
            return False
        except requests.exceptions.MissingSchema:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('Invaild Url @ '+ooxx['filename'])
            return False
        except requests.exceptions.TooManyRedirects:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('TooManyRedirects @ '+ooxx['filename'])
            return False

    def save_datas(self, ooxxs):
        for ooxx in ooxxs:
            self.save_one_data(ooxx)

    def delete_file(self, filename):
        if os.path.isfile(self.path+filename):
            os.remove(self.path+filename)

    def delete_old(self, ooxx):
        self.delete_file(ooxx['filename-old'])


    def download_image(ooxx):
        global save_Img, bar, errors
        if not save_Img.save_one_data(ooxx):
            errors.append(ooxx)
            mongo.get_table().update_one(
                filter={'_id': ooxx['_id']},
                update={'$set': {'status':-1}}
            )
        else:
            mongo.get_table().update_one(
                filter={'_id': ooxx['_id']},
                update={'$set': {'status':1}}
            )
        bar.move()
        bar.log('{0:0>4}'.format(ooxx['page']))

    def download(status=0):
        global save_Img, bar, errors
        errors = []
        save_Img = SaveImage(path)
        collection = mongo.get_datas_by('status',3)
        for img in collection:
            save_Img.delete_old(img)
        mongo.get_table().update(
            spec={'status':3},
            document={'$set': {'status':0}}
        )

        collection = mongo.get_datas_by('status',status)
        totalnum = collection.count()
        print('Total '+str(totalnum))
        bar = ProgressBar(total=totalnum)

        pool = ThreadPool(16)  # 创建一个线程池，16个线程数
        pool.map(download_image, collection)  # 将任务交给线程池，所有url都完成后再继续执行，与python的map方法类似

        print('Error Count : '+str(len(errors)))
