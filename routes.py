from flask import Flask, request, jsonify, render_template, redirect
from config import get_config, User, DataBase

app = Flask(__name__)
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
            return redirect ('/chat_users')
        else:
            return jsonify({'errore': 'il nome d utente o la password sono errati'})
        
    return render_template('login.html')

@app.route('/chat_users', methods=['GET','POST'])
def chat_users():
    user_id=None
    if request.method == 'GET':
        text = request.args.get('text')
        print (text)
        if text:
            user_id = DataBase.search_user(text)
        return render_template('chat_users.html', user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)
