from src.services.db import db;

tags = db.tags

def getAll():
    return tags.find()

def create(document):
    result = tags.insert_one(document)
    return str(result.inserted_id)
