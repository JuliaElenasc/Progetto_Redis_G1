import redis 
#cx= redis.Redis(host='localhost')

class Utente:
    def __init__(self, nome, password,status='Active'):
        self.nome = nome
        self.password = password
        self.status=status
        self.redis_db = redis.StrictRedis(
            host='redis-16811.c300.eu-central-1-1.ec2.cloud.redislabs.com',
            port=16811,
            password="6dAlNtEyjjzvzXX8DWYGK64QMvWBx21c",
            decode_responses=True
        )
        self.key_info_chat = f"Chat con:{self.nome}"

    def registro(self):
        info_chat = {
            "nome": self.nome,
            "password": self.password
        }
        self.redis_db.hmset(self.key_info_chat, info_chat)

    def login(self, nome, password):
        if nome in info_chat and password in info_chat:
            self.redis_db.hmset(self.key_info_chat + f"Chat con:{nome}")
    
    def lista_pasageri(self):
        keys = self.redis_db.keys(f"vuelo:{self.numero}:pasajeros:*")
        pasajeros = {}
        for key in keys:
            pasajeros[key] = self.redis_db.hgetall(key)
        return pasajeros
