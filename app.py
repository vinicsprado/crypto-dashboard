from flask import Flask, render_template_string
import requests

app = Flask(__name__)

@app.route('/')
def index():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin,ethereum,solana',
        'vs_currencies': 'usd,brl'
    }
    response = requests.get(url, params=params)
    data = response.json()

    html = '''
    <html>
    <head>
        <title>Crypto Dashboard</title>
        <meta http-equiv="refresh" content="60">
        <style>
            body { font-family: Arial; background-color: #111; color: #eee; text-align: center; }
            h1 { color: #00ff99; }
            table { margin: auto; border-collapse: collapse; }
            td, th { border: 1px solid #444; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>🪙 Preços de Criptomoedas</h1>
        <table>
            <tr><th>Criptomoeda</th><th>USD</th><th>BRL</th></tr>
            {% for coin, price in data.items() %}
            <tr>
                <td>{{ coin.capitalize() }}</td>
                <td>${{ price['usd'] }}</td>
                <td>R$ {{ price['brl'] }}</td>
            </tr>
            {% endfor %}
        </table>
        <p>Atualiza a cada 60 segundos.</p>
    </body>
    </html>
    '''
    return render_template_string(html, data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)