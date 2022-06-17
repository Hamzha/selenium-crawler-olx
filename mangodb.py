from pymongo import MongoClient
from bson.objectid import ObjectId

# mongodb://localhost:27017
# 'olx'


def connect_DB(db_link, db_name):

    cluster = MongoClient(db_link)
    mydb = cluster[db_name]
    return cluster, mydb


def delete_all_records(db, collection):
    db[collection].delete_many({})
    return True


def drop_collection(db, collection):
    db[collection].drop()
    return True


def insert_single_record(db, collection, record):
    db[collection].insert_one(record)
    return True


def get_all_records(db, collection):
    return db[collection].find()


def update_record(db, collection, id, record):
    db[collection].update_one({'_id': id}, {'$set': record})
    return True
