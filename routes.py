from flask import Flask, request, jsonify, render_template, redirect, session
from config import get_config, User, DataBase

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
    if request.method == 'GET':
        text = request.args.get('text')
        if text:
            user_id = DataBase.search_user(text)
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
        print(dnd) #estoy recibiendo bien on y of del frontend
        if dnd == 'on':
            DataBase.dnd_mode_t(username)
        else:
            DataBase.dnd_mode_f(username)
    return redirect('/chat_users')


if __name__ == '__main__':
    app.run(debug=True)
