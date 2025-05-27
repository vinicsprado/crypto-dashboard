import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pandas as pd
import requests
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('COINGECKO_API_KEY')

app = dash.Dash(__name__)
server = app.server

coins = {
    'bitcoin': 'Bitcoin',
    'ethereum': 'Ethereum',
    'solana': 'Solana',
    'cardano': 'Cardano',
    'polygon': 'Polygon'
}

def fetch_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': '1', 'interval': 'minute'}
    headers = {'x-cg-pro-api-key': API_KEY}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame(columns=['Time', 'Price'])
    data = response.json()
    prices = pd.DataFrame(data.get('prices', []), columns=['Time', 'Price'])
    prices['Time'] = pd.to_datetime(prices['Time'], unit='ms')
    return prices

def calculate_signals(df):
    if df.empty or len(df) < 15:
        return 'Sem Dados'
    df['SMA5'] = df['Price'].rolling(window=5).mean()
    df['SMA15'] = df['Price'].rolling(window=15).mean()
    if df['SMA5'].iloc[-1] > df['SMA15'].iloc[-1]:
        return 'Compra'
    elif df['SMA5'].iloc[-1] < df['SMA15'].iloc[-1]:
        return 'Venda'
    else:
        return 'Manter'

app.layout = html.Div([
    html.H1("🪙 Dashboard de Criptomoedas com IA", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='coin-dropdown',
        options=[{'label': name, 'value': coin} for coin, name in coins.items()],
        value='bitcoin',
        style={'width': '50%', 'margin': 'auto'}
    ),
    dcc.Graph(id='price-graph'),
    html.H2(id='signal-output', style={'textAlign': 'center', 'color': 'green'}),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])

@app.callback(
    [Output('price-graph', 'figure'),
     Output('signal-output', 'children')],
    [Input('coin-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graph(coin, n):
    df = fetch_prices(coin)
    signal = calculate_signals(df)

    if df.empty:
        figure = {
            'data': [],
            'layout': go.Layout(title='Dados não disponíveis', paper_bgcolor='#111', plot_bgcolor='#111', font={'color': '#FFFFFF'})
        }
        return figure, "Sem dados disponíveis"

    figure = {
        'data': [go.Scatter(x=df['Time'], y=df['Price'], mode='lines', name='Preço')],
        'layout': go.Layout(
            title=f'Preço de {coins[coin]} (USD)',
            xaxis={'title': 'Tempo'},
            yaxis={'title': 'Preço (USD)'},
            paper_bgcolor='#111111',
            plot_bgcolor='#111111',
            font={'color': '#FFFFFF'}
        )
    }

    return figure, f"Recomendação atual: {signal}"


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8080)