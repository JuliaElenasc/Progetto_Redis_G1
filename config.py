import json
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
    secret_key='12345'
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
        self.mode= True
        self.contacts=[]


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
                "mode": str(user.mode),
                "contacts" :json.dumps(user.contacts)
            }
            redis_db.hmset(user_key, user_details)
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
                'mode': user_details.get(b'mode')
            }
        else:
            return None
             
    @staticmethod
    def search_user(text):
        redis_db = get_config().redis_client
        matching_usernames=[]
        users= redis_db.keys(f'*{text}*' )
        for user in users:
            username = user.decode('utf-8').split(':')[-1]
            matching_usernames.append(username)
        return matching_usernames
    
    @staticmethod
    def contact_list(username):
        redis_db = get_config().redis_client
        user_key = f"user:{username}"
        contact_list= redis_db.lrange(f'{user_key}:contacts', 0, -1)
        contacts=[contact.decode('utf-8') for contact in contact_list]
        return contacts        

    @staticmethod
    def add_contact(username, contact):
        redis_db = get_config().redis_client
        user_key = f"user:{username}"
        redis_db.rpush(f'{user_key}:contacts', contact)
        return 'ok'

    @staticmethod # creo que no lo uso - verificar
    def get_contacts (username):
        redis_db = get_config().redis_client
        users_set = redis_db.smembers('users')
        users_set_str = [elemento.decode('utf-8') for elemento in users_set]
        print(users_set_str)
        return (users_set_str) 
    
    @staticmethod
    def dnd_mode_f(username):
        redis_db = get_config().redis_client
        user_key = f"user:{username}"
        dnd_mode = redis_db.hset(user_key, "mode", "False")
        print(dnd_mode)
        return dnd_mode
    
    @staticmethod
    def dnd_mode_t(username):
        redis_db = get_config().redis_client
        user_key = f"user:{username}"
        dnd_mode = redis_db.hset(user_key, "mode", "True")
        return dnd_mode