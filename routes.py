import datetime
from flask import Flask, Response, g, request, jsonify, render_template, redirect, session, url_for
from config import get_config, User, DataBase
import threading


app = Flask(__name__)
app.secret_key = '12345'
app.config.from_object(get_config())


@app.route('/')
def index():
    return render_template ('Index.html')

@app.route ('/registro')
def registro():
    return render_template ('registro.html')

@app.route('/add_registro', methods=['POST'])
def add_registro():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        if DataBase.user_exists(user):
            return jsonify({'errore': 'il nome d utente già esiste, prova un altro nome'})
        else: 
            utente = User(user, password)
            DataBase.insert_user(utente)
            return jsonify({'message': 'utente inserito con successo'})

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        data = DataBase.get_user(user, password)
        if data is not None:
            session['user']=user
            DataBase.dnd_mode_f(user) #l'utente inizia sempre con il modo dnd inattivo (false in db)
            return redirect ('/chat_users')
        else:
            return jsonify({'errore': 'il nome d utente o la password sono errati'})
        
    return render_template('login.html')

@app.route('/chat_users', methods=['GET','POST'])
def chat_users():
    user_id=None
    username=session.get('user')
    dettaglioUtente = username
    contacts = DataBase.contact_list(username)
    text = request.args.get('text')
    if text:
        user_id = DataBase.search_user(text)
    if request.method == 'GET':
        channel = request.args.get('channel')
        return render_template('chat_users.html', user_id=user_id, dettaglioUtente=dettaglioUtente, contacts=contacts, channel=channel)
    return render_template('chat_users.html', user_id=user_id, dettaglioUtente=dettaglioUtente, contacts=contacts)

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        username = session.get('user')
        contact= request.form.get('contact')
        print(contact)
        contacts=DataBase.contact_list(username)
        if contact not in contacts:
            DataBase.add_contact(username, contact)
            return redirect('/chat_users')
    return redirect('/chat_users')
    
@app.route ('/change_mode', methods=['POST'])  
def change_mode():
    username = session.get('user')
    if 'user' in session:
        dnd=request.form.get('mode')
        if dnd == 'on':
            DataBase.dnd_mode_t(username)
        else:
            DataBase.dnd_mode_f(username)
    return redirect('/chat_users')

@app.route ('/start_chat', methods=['POST']) #creo que no uso esta funcion
def start_chat ():
    if request.method == 'POST':
        username = session.get('user')
        contact= request.form.get('contact')
        channel=DataBase.subscribe_chat(username,contact)
        #print('chat channel', channel)
        session['channel'] = channel
        #print('session chanel',channel)
    return redirect ('/chat_users')

@app.route ('/channel', methods=['GET','POST'])
def channel():
    username=session.get('user')
    contact= request.args.get('contact')
    channel_name=f'{username}_{contact}'
    sort_letters = ''.join(sorted(channel_name.replace('_', '')))
    channel_sort = sort_letters[:len(sort_letters)//2] + '_' + sort_letters[len(sort_letters)//2:]
    #print(channel_sort)
    session['channel'] = channel_sort
    session['contact']=contact
    
    return redirect (url_for ('chat_users', channel=channel_sort))

@app.route('/post', methods=['POST', 'GET'])
def post():
    message = request.form['message']
    user = session.get('user')
    channel = session.get('channel')
    contact= session.get('contact')
    #print(contact)
    #print ('channel',channel) 
    chat=DataBase.publish_message(user, contact, channel, message)
    #print('chat:',chat)
    return Response(status=204)

@app.route('/stream', methods=['GET','POST'])
def stream():
    channel = session.get('channel') 
    #print ('channel stream',channel) 
    return Response(DataBase.event_stream(channel,10), mimetype="text/event-stream")
    
if __name__ == '__main__':
    app.run(debug=True)
