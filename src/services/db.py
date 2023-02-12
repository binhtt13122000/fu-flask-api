from pymongo import mongo_client

client = mongo_client.MongoClient("mongodb://root:example@localhost:27017/")

db = client["fu-app"]