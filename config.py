import redis
import os
from werkzeug.utils import import_string
from flask import Flask, request, jsonify

#Conessione al server
class Config(object):
    REDIS_HOST= 'redis-16811.c300.eu-central-1-1.ec2.cloud.redislabs.com'
    REDIS_PORT = 16811
    REDIS_PASSWORD = "6dAlNtEyjjzvzXX8DWYGK64QMvWBx21c"
    SESSION_TYPE = "redis"
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD
    )
    SESSION_REDIS = redis_client

class ConfigDev(Config):
    DEBUG = True

def get_config() -> Config:
    return ConfigDev

# Interazione con la DB
class User: 
    def __init__(self, username, password): 
        self.username = username 
        self.password = password
        self.active= True

class DataBase:
    @staticmethod 
    def user_exists(username):
        redis_db = get_config().redis_client
        return redis_db.sismember('user', username)
    
    @staticmethod 
    def insert_user(user):
        redis_db = get_config().redis_client
        if not DataBase.user_exists(user.username):
            user_key = f"user:{user.username}"
            user_details = {
                "password": user.password,
                "status": str(user.active)
            }
            redis_db.hmset(user_key, user_details)
            redis_db.sadd('users', user.username)
            return True
        
        return False

    @staticmethod 
    def get_user (username, password):
        redis_db = get_config().redis_client
        user_details = redis_db.hgetall(f"user:{username}")
        if user_details and user_details.get(b'password') == password.encode('utf-8'):
            return {
                'username': username,
                'password': password,
                'status': user_details.get(b'status')
            }
        else:
            return None

    @staticmethod #revisar la logica...
    def change_user_DND(username):
        user_key = f"user:{username}"
        redis_db = get_config().redis_client
        user_details = redis_db.hgetall(user_key)
        if not user_details:
            return False 
        user_details["active"] = "DND"
        redis_db.hmset(user_key, user_details)
        return True 
    
    @staticmethod #no es necesario
    def list_users ():
        redis_db = get_config().redis_client
        users_set = redis_db.smembers('users')
        users_set_str = [elemento.decode('utf-8') for elemento in users_set]
        print(users_set_str)
        return (users_set_str)
    
    @staticmethod
    def search_user(text):
        print('ok')
        redis_db = get_config().redis_client
        cursor=0
        matching_usernames=[]
        while True:
            cursor,users= redis_db.sscan('users', cursor, match=f'*{text}*' )
            print(users)
            matching_usernames=[elemento.decode('utf-8') for elemento in users]
            if cursor==0:
                break
        return matching_usernames