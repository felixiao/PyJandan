# -*- coding: utf-8-*-
import time, json, sys
from progressbar import ProgressBar
from parsehtml import HtmlParser
from mongohelper import MongoHelper
from saveimg import SaveImage
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool  # 线程池

global save_Img, bar, mongo, errors
path = './ooxx/'
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

if __name__ == '__main__':
    start = time.time()
    mongo = MongoHelper()
    if len(sys.argv)>1:
        download(int(sys.argv[1]))
    else:
        download(0)
    end = time.time()
    print('cost '+str(end-start))
