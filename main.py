from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyrebase
import requests
import json
import time
from main2 import app2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configuração do Firebase
config = {
    "apiKey": "AIzaSyC35Nx5PlqGFdGlx7OF-Hhks1pEQKAkoN8",
    "authDomain": "investidorprivate.firebaseapp.com",
    "databaseURL": "https://investidorprivate-default-rtdb.firebaseio.com",
    "projectId": "investidorprivate",
    "storageBucket": "investidorprivate.appspot.com",
    "messagingSenderId": "663117534406",
    "appId": "1:663117534406:web:489dd4ca3d2572b13e33c7",
    "measurementId": "G-2JSVE5BSMQ"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Rotas de Autenticação
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']
    
    try:
        user_info = auth.get_account_info(user_id)
        firebase_user_id = user_info['users'][0]['localId']
        
        user_info_ref = db.child("users").child(firebase_user_id).child("info")
        user_info_data = user_info_ref.get().val()
        
        if not user_info_data:
            print("Nenhum dado encontrado para o usuário.")
            return redirect(url_for('login'))
        
        name = user_info_data.get('name')
        perfil_investidor = user_info_data.get('perfilinvestidor')

        print(f"Nome do usuário: {name}")
        print(f"Perfil investidor: {perfil_investidor}")

        if name is None:
            return redirect(url_for('login'))
        
    except Exception as e:
        print(f"Erro ao buscar dados do usuário: {e}")
        return redirect(url_for('login'))

    return render_template('index.html', name=name, perfilinvestidor=perfil_investidor)


@app.route('/')
def first():
    return render_template('first.html')



@app.route('/iniciante')
def iniciante():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('iniciante.html')

@app.route('/intermediario')
def intermediario():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('intermediario.html')

@app.route('/avançado')
def avançado():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('avançado.html')

@app.route('/perfilinvestidor')
def perfilinvestidor():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('perfilinvestidor.html')

@app.route('/save_investor_profile', methods=['POST'])
def save_investor_profile():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = auth.get_account_info(session['user'])['users'][0]['localId']
    result = request.get_json().get('result')

    # Atualiza o campo `perfilinvestidor` com o resultado final
    db.child("users").child(user_id).child("info").update({
        "perfilinvestidor": result
    })
    
    return jsonify({'success': True})


@app.route('/indexcalculadora')
def indexcalculadora():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('indexcalculadora.html')

@app.route('/generic')
def generic():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('generic.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'register':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            # Adicione logs para verificar se os dados estão corretos
            print(f"Received registration request. Name: {name}, Email: {email}")

            try:
                # Cria um novo usuário
                user = auth.create_user_with_email_and_password(email, password)
                user_id = user['localId']
                
                # Verifique a criação do usuário e o ID
                print(f"User created with ID: {user_id}")

                # Salvar o nome do usuário no Firebase Realtime Database
                db.child("users").child(user_id).child("info").set({"name": name})
                
                # Verifique se os dados foram salvos corretamente
                saved_data = db.child("users").child(user_id).get().val()
                print(f"Saved data: {saved_data}")

                return "Registration successful. You can now log in."
            except Exception as e:
                print(f"Error during registration: {e}")
                return f"Error during registration: {e}"
        else:
            email = request.form['email']
            password = request.form['password']
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                session['user'] = user['idToken']
                return redirect(url_for('index'))
            except Exception as e:
                print(f"Login failed: {e}")
                return f"Login failed: {e}"
    return render_template('login.html')
    

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/indexcarteira')
def indexcarteira():
    # Verifica se o usuário está na sessão
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        # Obtém as informações da conta do usuário
        user_id = auth.get_account_info(session['user'])['users'][0]['localId']
        user_data = db.child("users").child(user_id).get().val()
        return render_template('indexcarteira.html', user_data=user_data)
    except requests.exceptions.HTTPError as e:
        # Verifica se o erro é um token inválido
        if hasattr(e, 'response') and e.response is not None:
            response = e.response
            if response.status_code == 400 and 'INVALID_ID_TOKEN' in response.text:
                # Redireciona para a página de login se o token for inválido
                return redirect(url_for('login'))
        # Para outros erros HTTP, re-levanta a exceção
        raise

# Rotas da API
@app.route('/get_quote', methods=['POST'])
def get_quote():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    symbol = request.form['symbol']
    token = 'xoAToPKAai8jfSwukJspez'  # Substitua 'your_api_token' pelo seu token da API real do brapi.dev
    url = f'https://brapi.dev/api/quote/{symbol}?token={token}'
    try:
        print("API Request URL:", url)
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção para códigos de status 4xx ou 5xx
        data = response.json()
        print("API Response:", data)
        if 'results' in data and data['results']:
            result = data['results'][0]
            result['id'] = symbol + str(int(time.time()))  # Cria um ID único
            return jsonify(result)
        else:
            return jsonify({'error': 'Price not found in API response'})
    except Exception as e:
        print("Error fetching quote:", e)
        return jsonify({'error': 'Failed to fetch quote. Please try again later.'}), 500
    

#parte do grafico

@app.route('/indexgrafico')
def indexgrafico():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('indexgrafico.html')

@app.route('/get_quote2', methods=['POST'])
def get_quote2():
    data = request.json
    symbol = data.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400

    token = 'xoAToPKAai8jfSwukJspez'  # Substitua pelo seu token da API real
    url = f'https://brapi.dev/api/quote/{symbol}?range=3mo&interval=1d&token={token}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        api_data = response.json()

        # Log da resposta para depuração
        print("API Response:", api_data)

        # Verificar se 'results' está presente e contém dados
        if 'results' in api_data and len(api_data['results']) > 0:
            result = api_data['results'][0]
            historical_data = result.get('historicalDataPrice', [])

            # Formatar os dados para o gráfico
            formatted_data = [{
                'date': item['date'],
                'open': item['open'],
                'high': item['high'],
                'low': item['low'],
                'close': item['close']
            } for item in historical_data]

            return jsonify({
                'symbol': result['symbol'],
                'historicalDataPrice': formatted_data
            })
        else:
            return jsonify({'error': 'No results found in API response'})
    except requests.RequestException as e:
        print("Error fetching quote:", e)
        return jsonify({'error': 'Failed to fetch quote. Please try again later.'}), 500

#-----------   

@app.route('/save_data', methods=['POST'])
def save_data():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = auth.get_account_info(session['user'])['users'][0]['localId']
    data = request.get_json()
    db.child("users").child(user_id).child("carteira").set(data)
    return jsonify({'success': True})

@app.route('/load_data', methods=['GET'])
def load_data():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = auth.get_account_info(session['user'])['users'][0]['localId']
    user_data = db.child("users").child(user_id).child("carteira").get().val()
    return jsonify(user_data)

@app.route('/delete_data', methods=['POST'])
def delete_data():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = auth.get_account_info(session['user'])['users'][0]['localId']
    data = request.get_json()
    item_id = data['id']
    db.child("users").child(user_id).child("carteira").child(item_id).remove()
    return jsonify({'success': True})


#parte do codigo stock

@app.route('/indexaçao')
def indexaçao():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('indexaçao.html')

@app.route('/show_stock_info', methods=['GET', 'POST'])
def show_stock_info():
    
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    symbol = data.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400

    token = 'xoAToPKAai8jfSwukJspez'
    url = f'https://brapi.dev/api/quote/{symbol}?token={token}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'results' in data and data['results']:
            result = data['results'][0]
            result['id'] = symbol + str(int(time.time()))
            return jsonify(result)
        else:
            return jsonify({'error': 'Price not found in API response'})
    except Exception as e:
        return jsonify({'error': 'Failed to fetch quote. Please try again later.'}), 500
    
app.register_blueprint(app2)

if __name__ == '__main__':
    app.run(debug=True)
