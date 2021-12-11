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
            'points': 0,
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
            'downvotes': [],
            'comments': [],
            'answers': []
        })
        self.users.update_one({'_id': user['_id']}, {'$push': {'questions': id}}, upsert=True)
        
    def getMostUpvotedQuestions(self):
        return [question for question in self.questions.find().sort('upvotes', -1).limit(10)]
    
    def getQuestion(self, id):
        return self.questions.find_one({'_id': id})
    
    def upvoteQuestion(self, id, user):
        question = self.getQuestion(id)
        if user not in question['upvotes']:
            self.questions.update_one({'_id': id}, {'$push': {'upvotes': user}})
            self.users.update_one({'_id': question['user']}, {'$inc': {'points': 1}}, upsert=True)
            self.users.update_one({'_id': user}, {'$push': {'upvoted': id}}, upsert=True)
            return True
        return False
    
    def removeUpvote(self, id, user):
        question = self.getQuestion(id)
        if user in question['upvotes']:
            self.questions.update_one({'_id': id}, {'$pull': {'upvotes': user}})
            self.users.update_one({'_id': question['user']}, {'$inc': {'points': -1}}, upsert=True)
            self.users.update_one({'_id': user}, {'$pull': {'upvoted': id}}, upsert=True)
            return True
        return False
    
    def downvoteQuestion(self, id, user):
        question = self.getQuestion(id)
        if user not in question['downvotes']:
            self.questions.update_one({'_id': id}, {'$push': {'downvotes': user}})
            self.users.update_one({'_id': question['user']}, {'$inc': {'points': -1}}, upsert=True)
            self.users.update_one({'_id': user}, {'$push': {'downvoted': id}}, upsert=True)
            return True
        return False
    
    def removeDownvote(self, id, user):
        question = self.getQuestion(id)
        if user in question['downvotes']:
            self.questions.update_one({'_id': id}, {'$pull': {'downvotes': user}})
            self.users.update_one({'_id': question['user']}, {'$inc': {'points': 1}}, upsert=True)
            self.users.update_one({'_id': user}, {'$pull': {'downvoted': id}}, upsert=True)
            return True
        return False
    
        