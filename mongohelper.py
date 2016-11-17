# -*- coding: utf-8-*-
import sys, json, datetime, time
from pymongo import MongoClient

class MongoHelper:
    def __init__(self):
        self.client = MongoClient()# MongoClient是线程安全的且内部维护了一个连接池，所以全局使用一个即可
        self.db = self.client['jandan']

    def get_db(self):
        return self.db

    def get_table(self):
        return self.db['ooxx']

    def insert_one(self,data):
        data['updateTime'] = datetime.datetime.utcnow()  # 我们最好记录下更新的时间
        data['status'] = 0
        ooxx = self.db['ooxx'].find_one({'_id':data['_id']})
        if ooxx is None:
            ooxx = self.db['ooxx'].insert(data)
        else:
            if ooxx['status'] == 0: # 未下载
                ooxx = self.db['ooxx'].update_one(
                    filter={'_id': data['_id']},
                    update={'$set': data}
                )
            elif ooxx['status'] == -1: # 下载错误
                data['status'] = -1
                ooxx = self.db['ooxx'].update_one(
                    filter={'_id': data['_id']},
                    update={'$set': data}
                )
            else:
                if ooxx['oo'] != data['oo'] and ooxx['xx'] != data['xx']: #已下载 有更新
                    old_filename = ooxx['filename']
                    ooxx = self.db['ooxx'].update_one(
                        filter={'_id': data['_id']},
                        update={'$set': {'status':3,
                                         'oo':data['oo'],
                                         'xx':data['xx'],
                                         'filename':data['filename'],
                                         'filename-old':old_filename,
                                         'updateTime':data['updateTime']}}
                    )
                else: # 已下载 无更新
                    ooxx = self.db['ooxx'].update_one(
                        filter={'_id': data['_id']},
                        update={'$set': {'status':2,
                                         'oo':data['oo'],
                                         'xx':data['xx'],
                                         'filename':data['filename'],
                                         'updateTime':data['updateTime']}}
                    )

    def insert_multi(self,data):
        for d in data:
            self.insert_one(d)

    def get_one_by_id(self,id):
        ooxx = self.db['ooxx'].find_one({'_id':id})
        print(ooxx)
        return ooxx

    def get_all(self):
        return self.db['ooxx'].find()

    def get_datas_by(self,key,value):
        results = self.db['ooxx'].find({key:value})
        return results

    def update_one(self,data):
        ooxx = self.db['ooxx'].update_one(
            filter={'_id': data['_id']},
            update={'$set': data},
            upsert=True
        )
        sys.stdout.write(' ' * 79 + '\r')
        sys.stdout.write(ooxx['_id']+' updated!')
        return ooxx

    def delete_one_by_id(self,id):
        ooxx = self.db['ooxx'].remove({'_id':id})
        sys.stdout.write(' ' * 79 + '\r')
        sys.stdout.write(ooxx['_id']+" deleted!")

    def clear(self):
        self.db['ooxx'].remove({})

    def read(self, data):
        self.insert_multi(data)
