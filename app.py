from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import socket

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'

def get_local_ip():
    try:
        # Crée une socket pour connecter au serveur Google's DNS
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception as e:
        print(f"Error obtaining local IP: {e}")
        return

local_ip = get_local_ip()

# Route pour la page de connexion ou d'accueil
@app.route('/')
def home():
    return render_template('login.html')  # Assurez-vous que le fichier 'login.html' existe dans le dossier templates


@app.route('/register')
def register():
    return render_template('register.html')

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Requête au backend pour authentifier l'utilisateur en envoyant les données en JSON
        response = requests.post(
            'http://localhost:8080/api/auth/login',
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            session['username'] = username
            session['password'] = password
            session['local_ip'] = local_ip
            return redirect(url_for('chat'))
        else:
            return "Échec de l'authentification", 401

    return render_template('login.html')

# Page de messagerie
@app.route('/chat')
def chat():
    global local_ip
    print(session)
    username = ""
    password = ""
    local_ip = local_ip
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'username' in session:
        username = session['username']
        password = session['password']
        local_ip = session['local_ip']
    print(username)
    print(password)
    return render_template('chat.html', username=username, password=password, local_ip=local_ip)

# Obtenir la liste des utilisateurs connectés
@app.route('/users')
def get_users():
    # Requête au backend pour obtenir la liste des utilisateurs
    response = requests.get('http://localhost:8080/api/auth/status/all')  # Vous devrez ajuster cette route dans le backend
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify([]), 400

# Envoyer un message
@app.route('/send_message', methods=['POST'])
def send_message():
     # Récupérer le message et l'utilisateur à partir de la requête JSON
    data = request.get_json()
    message = data.get('message')
    groupId = data.get('groupId')
    username = session.get('username')  # Récupérer l'utilisateur connecté depuis la session
    password = session.get('password')  # Récupérer l'utilisateur connecté depuis la session

    if not message or not username:
        return jsonify({"message": "Données manquantes"}), 400
    
    # Ajouter les informations d'authentification dans la requête
    auth = (username, password)  # Le mot de passe est celui que vous avez configuré pour cet utilisateur


    # Requête pour envoyer un message via le backend
    response = requests.post('http://localhost:8080/api/messages/send', json={
        'senderId': username,
        'messageContent': message,
        'recipientId': 'user2',  # Vous devrez adapter cela pour envoyer à un autre utilisateur
        'groupId': groupId,  # Vous devrez adapter cela pour envoyer à un autre utilisateur
    }, auth=auth)

    print(response)

    if response.status_code == 200:
        return jsonify({"message": "Message envoyé avec succès"})
    else:
        return jsonify({"message": "Erreur lors de l'envoi du message"}), 400


@app.route('/get_messages', methods=['GET'])
def get_messages():
    # Vous pouvez ajouter une authentification ici si nécessaire
    return jsonify(messages), 200

if __name__ == "__main__":
    app.run(debug=True)