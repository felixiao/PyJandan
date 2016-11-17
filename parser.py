# -*- coding: utf-8-*-
import time, json, sys
from progressbar import ProgressBar
from parsehtml import HtmlParser
from mongohelper import MongoHelper
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool  # 线程池

if __name__ == '__main__':
    start = time.time()
    mongo = MongoHelper()
    parser = HtmlParser()
    if len(sys.argv) <=1:
        parser.parse(count=20)
    if sys.argv[1].lower() == '-r':
        parser.parse(range=[int(sys.argv[2]),int(sys.argv[3])])
    elif sys.argv[1].lower() == '-c':
        parser.parse(count=int(sys.argv[2]))
    else:
        print('参数错误: parser.py 或 parser.py -r 1 2 或 parser.py -c 1')
    mongo.read(parser.get_data())
    end = time.time()
    print('cost '+str(end-start))
