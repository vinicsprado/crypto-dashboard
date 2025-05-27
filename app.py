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

chart_options = ['Linha', 'Candlestick']

def fetch_prices(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {'vs_currency': 'usd', 'days': '1'}
    headers = {'x-cg-pro-api-key': API_KEY}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close'])
    data = response.json()
    df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close'])
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    return df

def calculate_indicators(df):
    df['SMA5'] = df['Close'].rolling(window=5).mean()
    df['SMA15'] = df['Close'].rolling(window=15).mean()
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA15'] + (df['STD'] * 2)
    df['Lower_Band'] = df['SMA15'] - (df['STD'] * 2)
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=14).mean()
    ma_down = down.rolling(window=14).mean()
    rs = ma_up / ma_down
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def generate_signal(df):
    if df.empty or len(df) < 15:
        return 'Sem Dados'
    if df['SMA5'].iloc[-1] > df['SMA15'].iloc[-1]:
        return 'Compra'
    elif df['SMA5'].iloc[-1] < df['SMA15'].iloc[-1]:
        return 'Venda'
    else:
        return 'Manter'

app.layout = html.Div([
    html.H1("🪙 Dashboard Cripto Pro com IA", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='coin-dropdown',
        options=[{'label': name, 'value': coin} for coin, name in coins.items()],
        value='bitcoin',
        style={'width': '50%', 'margin': 'auto'}
    ),
    dcc.RadioItems(
        id='chart-type',
        options=[{'label': opt, 'value': opt} for opt in chart_options],
        value='Linha',
        labelStyle={'display': 'inline-block', 'marginRight': '20px'},
        style={'textAlign': 'center', 'marginBottom': '20px'}
    ),
    dcc.Graph(id='price-graph'),
    html.H2(id='signal-output', style={'textAlign': 'center', 'color': 'green'}),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
])

@app.callback(
    [Output('price-graph', 'figure'),
     Output('signal-output', 'children')],
    [Input('coin-dropdown', 'value'),
     Input('chart-type', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graph(coin, chart_type, n):
    df = fetch_prices(coin)
    df = calculate_indicators(df)
    signal = generate_signal(df)

    if df.empty:
        figure = {
            'data': [],
            'layout': go.Layout(title='Dados não disponíveis', paper_bgcolor='#111', plot_bgcolor='#111', font={'color': '#FFFFFF'})
        }
        return figure, "Sem dados disponíveis"

    if chart_type == 'Linha':
        data = [
            go.Scatter(x=df['Time'], y=df['Close'], mode='lines', name='Preço'),
            go.Scatter(x=df['Time'], y=df['Upper_Band'], line={'dash': 'dot'}, name='Banda Superior'),
            go.Scatter(x=df['Time'], y=df['Lower_Band'], line={'dash': 'dot'}, name='Banda Inferior'),
            go.Scatter(x=df['Time'], y=df['SMA15'], line={'dash': 'dot'}, name='Média Móvel 15')
        ]
    else:
        data = [go.Candlestick(
            x=df['Time'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick'
        )]

    figure = {
        'data': data,
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