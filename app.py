import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('CG-rcWHrATZzuhrgSZjFo1o3bwS')

app = dash.Dash(__name__)
server = app.server

# Configurações de moedas
coins = {
    'bitcoin': 'Bitcoin',
    'ethereum': 'Ethereum'
}

# Configurações de períodos
period_options = {
    '1': '1 dia',
    '7': '7 dias',
    '30': '30 dias',
    '90': '90 dias',
    '180': '180 dias',
    '365': '365 dias',
    '730': '2 anos'
}

# ================== Funções ==================

def fetch_data(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': days, 'interval': 'hourly'}
    headers = {'x-cg-pro-api-key': API_KEY}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame()

    data = response.json()
    df = pd.DataFrame(data['prices'], columns=['Time', 'Price'])
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    return df


def calculate_indicators(df, sma_window, ema_window, rsi_window, boll_window):
    df = df.copy()
    df['SMA'] = df['Price'].rolling(window=sma_window).mean()
    df['EMA'] = df['Price'].ewm(span=ema_window, adjust=False).mean()

    # RSI
    delta = df['Price'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=rsi_window).mean()
    ma_down = down.rolling(window=rsi_window).mean()
    rs = ma_up / ma_down
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['STD'] = df['Price'].rolling(window=boll_window).std()
    df['Upper'] = df['SMA'] + (df['STD'] * 2)
    df['Lower'] = df['SMA'] - (df['STD'] * 2)

    return df


def backtest_strategy(df):
    df = df.copy()
    df['SMA5'] = df['Price'].rolling(window=5).mean()
    df['SMA15'] = df['Price'].rolling(window=15).mean()

    df['Position'] = 0
    df.loc[df['SMA5'] > df['SMA15'], 'Position'] = 1
    df.loc[df['SMA5'] < df['SMA15'], 'Position'] = -1
    df['Signal'] = df['Position'].diff()

    df['Return'] = df['Price'].pct_change()
    df['Strategy'] = df['Position'].shift(1) * df['Return']
    df['Cumulative'] = (1 + df['Strategy'].fillna(0)).cumprod()

    trades = df['Signal'].abs().sum() / 2
    total_return = df['Cumulative'].iloc[-1] - 1
    win_trades = (df['Strategy'] > 0).sum()
    lose_trades = (df['Strategy'] < 0).sum()

    return df, {
        'Total Return': round(total_return * 100, 2),
        'Trades': int(trades),
        'Wins': int(win_trades),
        'Losses': int(lose_trades)
    }

# ================== Layout ==================

app.layout = html.Div([
    html.H1('🪙 Crypto Dashboard', style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H3('Configurações Moeda 1'),
            dcc.Dropdown(
                id='coin1',
                options=[{'label': v, 'value': k} for k, v in coins.items()],
                value='bitcoin'
            ),
            dcc.Dropdown(
                id='period1',
                options=[{'label': v, 'value': k} for k, v in period_options.items()],
                value='7'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.H3('Configurações Moeda 2'),
            dcc.Dropdown(
                id='coin2',
                options=[{'label': v, 'value': k} for k, v in coins.items()],
                value='ethereum'
            ),
            dcc.Dropdown(
                id='period2',
                options=[{'label': v, 'value': k} for k, v in period_options.items()],
                value='7'
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Label('Tipo de Gráfico'),
        dcc.RadioItems(
            id='chart-type',
            options=[
                {'label': 'Linha', 'value': 'line'},
                {'label': 'Candlestick', 'value': 'candle'}
            ],
            value='line',
            labelStyle={'display': 'inline-block'}
        ),
    ], style={'textAlign': 'center'}),

    html.Div([
        dcc.Graph(id='graph1'),
        dcc.Graph(id='graph2')
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    html.Div(id='backtest-output'),

    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 1 minuto
        n_intervals=0
    )
])


# ================== Callbacks ==================

@app.callback(
    [Output('graph1', 'figure'),
     Output('graph2', 'figure'),
     Output('backtest-output', 'children')],
    [Input('coin1', 'value'),
     Input('period1', 'value'),
     Input('coin2', 'value'),
     Input('period2', 'value'),
     Input('chart-type', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graph(coin1, period1, coin2, period2, chart_type, n):

    df1 = fetch_data(coin1, period1)
    df2 = fetch_data(coin2, period2)

    df1 = calculate_indicators(df1, 15, 20, 14, 20)
    df2 = calculate_indicators(df2, 15, 20, 14, 20)

    df1_bt, stats1 = backtest_strategy(df1)
    df2_bt, stats2 = backtest_strategy(df2)

    # Gráfico 1
    fig1 = go.Figure()
    if chart_type == 'line':
        fig1.add_trace(go.Scatter(x=df1['Time'], y=df1['Price'], name='Preço'))
        fig1.add_trace(go.Scatter(x=df1['Time'], y=df1['Upper'], name='Bollinger Upper'))
        fig1.add_trace(go.Scatter(x=df1['Time'], y=df1['Lower'], name='Bollinger Lower'))
    else:
        fig1.add_trace(go.Candlestick(
            x=df1['Time'],
            open=df1['Price'],
            high=df1['Price'],
            low=df1['Price'],
            close=df1['Price'],
            name='Candlestick'
        ))

    fig1.update_layout(title=coins[coin1])

    # Gráfico 2
    fig2 = go.Figure()
    if chart_type == 'line':
        fig2.add_trace(go.Scatter(x=df2['Time'], y=df2['Price'], name='Preço'))
        fig2.add_trace(go.Scatter(x=df2['Time'], y=df2['Upper'], name='Bollinger Upper'))
        fig2.add_trace(go.Scatter(x=df2['Time'], y=df2['Lower'], name='Bollinger Lower'))
    else:
        fig2.add_trace(go.Candlestick(
            x=df2['Time'],
            open=df2['Price'],
            high=df2['Price'],
            low=df2['Price'],
            close=df2['Price'],
            name='Candlestick'
        ))

    fig2.update_layout(title=coins[coin2])

    backtest_output = html.Div([
        html.H3('Backtesting Resultados'),
        html.P(f"{coins[coin1]} - Return: {stats1['Total Return']}%, Trades: {stats1['Trades']}, Wins: {stats1['Wins']}, Losses: {stats1['Losses']}"),
        html.P(f"{coins[coin2]} - Return: {stats2['Total Return']}%, Trades: {stats2['Trades']}, Wins: {stats2['Wins']}, Losses: {stats2['Losses']}")
    ])

    return fig1, fig2, backtest_output


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
