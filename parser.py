# -*- coding: utf-8-*-
import time, json, sys, csv
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
    list_of_rows=[]
    for row in parser.get_data():
        list_of_cells=[]
        list_of_cells.append(row['_id'])
        list_of_cells.append(row['updateTime'])
        list_of_cells.append(row['status'])
        list_of_cells.append(row['oo'])
        list_of_cells.append(row['xx'])
        list_of_cells.append(row['author'])
        list_of_cells.append(row['page'])
        list_of_cells.append(row['rate'])
        list_of_cells.append(row['rating'])
        list_of_cells.append(row['url'])
        list_of_cells.append(row['filename'])
        list_of_cells.append(row['ext'])
        list_of_rows.append(list_of_cells)

    with open('imgs.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(['_id', 'updateTime', 'status','oo', 'xx', 'author', 'page', 'rate', 'rating', 'url', 'filename','ext'])
        spamwriter.writerows(list_of_rows)

    list_of_errors=[]
    for row in parser.get_errors():
        list_of_cells=[]
        list_of_cells.append(row['_id'])
        list_of_cells.append(row['author'])
        list_of_cells.append(row['page'])
        list_of_cells.append(row['error'])
        list_of_errors.append(list_of_cells)

    with open('errors.csv', 'w') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(['_id', 'author', 'page','error'])
        spamwriter.writerows(list_of_errors)
