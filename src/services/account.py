from src.services.db import db

accounts = db.accounts


def findByEmail(email: str):
    return accounts.find_one({
        "email": email
    },
        {'_id': False}
    )


def create(document):
    result = accounts.insert_one(document)
    return str(result.inserted_id)
