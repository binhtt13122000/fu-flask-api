from pymongo import mongo_client

client = mongo_client.MongoClient("mongodb://root:example@mongo:27017/")

db = client["fu-app"]