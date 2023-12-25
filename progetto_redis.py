import redis
from datetime import datetime, timedelta
import threading
import time
import json


# Connessione a Redis
redis_conn = redis.StrictRedis(host='redis-17515.c250.eu-central-1-1.ec2.cloud.redislabs.com',
                               port=17515,
                               password="bspCqFANduy7b8nheVwZJfA0eQ4jrbuc",
                               decode_responses=True)

def menu():
    print("Benvenuto! Cosa vuoi fare?")
    print("1. Registrati")
    print("2. Effettua il login")

    choice = input("Scelta: ")

    if choice == '1':
        register_user()
    elif choice == '2':
        username = input("Inserisci il nome utente: ")
        login(username)
    else:
        print("Scelta non valida. Riprova.")
        return False

def register_user():
    # Ottieni l'input dell'utente per la registrazione
    username = input("Inserisci il nome utente: ")
    password = input("Inserisci la password: ")

    # Verifica se l'utente esiste già
    if redis_conn.hexists('users', username):
        print(f"Errore: L'utente '{username}' esiste già.")
        return False

    # Salva le informazioni dell'utente in Redis
    user_data = {'password': password, 'contacts': list(), 'dnd_mode': 'off'}
    redis_conn.hset('users', username, json.dumps(user_data))

    print(f"Registrazione completata per l'utente '{username}'.")
    return True

def login(username):
    # Verifica se l'utente esiste
    if not redis_conn.hexists('users', username):
        print("Errore: Nome utente non trovato.")
        return None

    print(f"Login effettuato per l'utente '{username}'.")
    return username




# def register_user():
#     # Ottieni l'input dell'utente per la registrazione
#     username = input("Inserisci il nome utente: ")
#     password = input("Inserisci la password: ")
#
#     # Verifica se l'utente esiste già
#     if redis_conn.hexists('users', username):
#         print(f"Errore: L'utente '{username}' esiste già.")
#         return False
#
#     # Salva le informazioni dell'utente in Redis
#     user_data = {'password': password, 'contacts': list(), 'dnd_mode': 'off'}
#     redis_conn.hset('users', username, json.dumps(user_data))
#
#     print(f"Registrazione completata per l'utente '{username}'.")
#     return True


# def login(username):
#     # Verifica se l'utente esiste
#     if not redis_conn.hexists('users', username):
#         print("Errore: Nome utente non trovato.")
#         return None
#
#     print(f"Login effettuato per l'utente '{username}'.")
#     return username


def search_users(query):
    # Cerca utenti che corrispondono al nome utente (anche parziale)
    matching_users = [user for user in redis_conn.hkeys('users') if query.lower() in user.lower()]
    return matching_users


def add_contact(username, contact_username):
    # Aggiunge un utente alla lista contatti dell'utente
    redis_conn.sadd(f'{username}:contacts', contact_username)
    print(f"Utente '{contact_username}' aggiunto alla lista contatti di '{username}'.")


def set_do_not_disturb(username, dnd_mode):
    # Imposta la modalità Do Not Disturb per l'utente
    redis_conn.hset('dnd', username, dnd_mode)
    print(f"Modalità Do Not Disturb impostata a '{dnd_mode}' per l'utente '{username}'.")


def send_message(sender, receiver, message):
    # Controlla se il destinatario è in modalità Do Not Disturb
    dnd_mode = redis_conn.hget('dnd', receiver)
    if dnd_mode and dnd_mode.lower() == 'on':
        print(f"Errore: L'utente '{receiver}' è in modalità Do Not Disturb. Il messaggio non è stato recapitato.")
    else:
        # Salva il messaggio nella chat dell'utente
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{timestamp} > {message}"
        redis_conn.zadd(f'{sender}:{receiver}:messages', {msg: 0})

        # Aggiungi una scadenza (1 minuto) alla chiave della chat
        redis_conn.expire(f'{sender}:{receiver}:messages', 60)

        # Invia una notifica push
        redis_conn.publish(f'notification:{receiver}', f"Nuovo messaggio da {sender}")


def read_messages(user1, user2):
    # Legge i messaggi inviati e ricevuti ordinati per data
    messages = redis_conn.zrevrange(f'{user1}:{user2}:messages', 0, -1, withscores=True)
    for msg, timestamp in messages:
        prefix = ">" if "> " in msg else "< "
        print(f"{prefix}{msg.strip(' ><')} [{datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}]")


def publish_message(sender, receiver, message):
    # Invia il messaggio nella chat dell'utente
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"{timestamp} > {message}"
    redis_conn.zadd(f'{sender}:{receiver}:messages', {msg: 0})

    # Aggiungi una scadenza (1 minuto) alla chiave della chat
    redis_conn.expire(f'{sender}:{receiver}:messages', 60)

    # Invia una notifica push
    redis_conn.publish(f'notification:{receiver}', f"Nuovo messaggio da {sender}")


def subscribe_notifications(username):
    # Iscriviti al canale di notifiche push
    pubsub = redis_conn.pubsub()
    pubsub.subscribe([f'notification:{username}'])

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Notifica push: {message['data']}")


# Esempio di utilizzo
menu()
register_user()
register_user()
#
# logged_in_user = login('')
#
# if logged_in_user:
#     add_contact(logged_in_user, '')
#     add_contact(logged_in_user, '')
#
#     set_do_not_disturb(logged_in_user, 'off')
#
#
#     # Avvia il thread per ascoltare le notifiche push
#     notification_thread = threading.Thread(target=subscribe_notifications, args=(logged_in_user,), daemon=True)
#     notification_thread.start()
#
#     # Attesa per consentire alla notifica push di essere ricevuta prima di terminare il programma
#     notification_thread.join()
