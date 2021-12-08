from pymongo import MongoClient
from uuid import uuid4
import random
import datetime
import requests
import config

class Database:
    def __init__(self):
        self.client = MongoClient(config.MONGO_URL)
        self.db = self.client.TheForum
        self.users = self.db.users
        self.questions = self.db.questions
        
    def addUser(self, email):
        name = email.split('@')[0]
        id =str(uuid4())
        token = str(uuid4())
        self.users.insert_one({
            '_id': id,
            'username': name,
            'avatar': f"https://avatars.dicebear.com/api/bottts/{id}.svg",
            'email': email,
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })
    
    def userExists(self, email):
        return self.users.find_one({'email': email}) is not None
    
    def getUser(self, email):
        return self.users.find_one({'email': email})
    
    def getUserWithId(self, id):
        return self.users.find_one({'_id': id})
    
    def updateName(self, email, name):
        self.users.update_one({'email': email}, {'$set': {'username': name}})
        return True
    
    def postQuestion(self, email, title, body, tags):
        user = self.getUser(email)
        id = str(uuid4())
        self.questions.insert_one({
            '_id': id,
            'title': title,
            'body': body,
            'tags': tags,
            'user': user['_id'],
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p"),
            'upvotes': [],
            'comments': [],
            'answers': []
        })
        self.users.update_one({'_id': user['_id']}, {'$push': {'questions': id}}, upsert=True)
        