import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests

# 🔑 Chave da API da CoinGecko
API_KEY = 'CG-rcWHrATZzuhrgSZjFo1o3bwS'

app = dash.Dash(__name__)
server = app.server

# 🎯 Configurações de moedas
coins = {
    'bitcoin': 'Bitcoin',
    'ethereum': 'Ethereum'
}

# 📆 Períodos possíveis
period_options = {
    '1': '1 dia',
    '7': '7 dias',
    '30': '30 dias',
    '90': '90 dias',
    '180': '180 dias',
    '365': '365 dias',
    '730': '2 anos'
}


# 🔗 Função para buscar dados da API
def fetch_data(coin_id, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': days}
    headers = {'x-cg-pro-api-key': API_KEY}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Erro na API: {response.status_code}")
        return pd.DataFrame()

    data = response.json()
    if 'prices' not in data or len(data['prices']) == 0:
        print(f"Sem dados para {coin_id}")
        return pd.DataFrame()

    df = pd.DataFrame(data['prices'], columns=['Time', 'Price'])
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    return df


# 🧠 Função para cálculo de indicadores técnicos
def calculate_indicators(df, sma_window, ema_window, rsi_window, boll_window):
    if df.empty or 'Price' not in df.columns:
        print("DataFrame vazio ou sem coluna 'Price'.")
        return df

    df = df.copy()
    df['SMA'] = df['Price'].rolling(window=sma_window).mean()
    df['EMA'] = df['Price'].ewm(span=ema_window, adjust=False).mean()

    delta = df['Price'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=rsi_window).mean()
    ma_down = down.rolling(window=rsi_window).mean()
    rs = ma_up / ma_down
    df['RSI'] = 100 - (100 / (1 + rs))

    df['STD'] = df['Price'].rolling(window=boll_window).std()
    df['Upper'] = df['SMA'] + (df['STD'] * 2)
    df['Lower'] = df['SMA'] - (df['STD'] * 2)

    return df


# 🏦 Backtesting simples baseado em cruzamento de médias
def backtest_strategy(df):
    if df.empty:
        return df, {'Total Return': 0, 'Trades': 0, 'Wins': 0, 'Losses': 0}

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
    total_return = df['Cumulative'].iloc[-1] - 1 if not df['Cumulative'].empty else 0
    win_trades = (df['Strategy'] > 0).sum()
    lose_trades = (df['Strategy'] < 0).sum()

    return df, {
        'Total Return': round(total_return * 100, 2),
        'Trades': int(trades),
        'Wins': int(win_trades),
        'Losses': int(lose_trades)
    }


# 🚦 Função para recomendação de compra, venda ou manter
def get_signal(df):
    if df.empty or 'SMA5' not in df.columns or 'SMA15' not in df.columns:
        return 'Sem dados'
    if df['SMA5'].iloc[-1] > df['SMA15'].iloc[-1]:
        return 'COMPRA'
    elif df['SMA5'].iloc[-1] < df['SMA15'].iloc[-1]:
        return 'VENDA'
    else:
        return 'MANTER'


# ======================= Layout ========================

app.layout = html.Div([
    html.H1('🪙 Crypto Dashboard', style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H4('Moeda 1'),
            dcc.Dropdown(
                id='coin1',
                options=[{'label': v, 'value': k} for k, v in coins.items()],
                value='bitcoin'
            ),
            html.H4('Período'),
            dcc.Dropdown(
                id='period1',
                options=[{'label': v, 'value': k} for k, v in period_options.items()],
                value='7'
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.H4('Moeda 2'),
            dcc.Dropdown(
                id='coin2',
                options=[{'label': v, 'value': k} for k, v in coins.items()],
                value='ethereum'
            ),
            html.H4('Período'),
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
        interval=60*1000,  # Atualiza a cada minuto
        n_intervals=0
    )
])


# ======================= Callback ========================

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

    signal1 = get_signal(df1_bt)
    signal2 = get_signal(df2_bt)

    def build_figure(df, coin_name):
        fig = go.Figure()
        if df.empty:
            fig.update_layout(title=f'{coin_name} - Sem dados disponíveis')
            return fig

        if chart_type == 'line':
            fig.add_trace(go.Scatter(x=df['Time'], y=df['Price'], name='Preço'))
            fig.add_trace(go.Scatter(x=df['Time'], y=df['Upper'], name='Bollinger Upper'))
            fig.add_trace(go.Scatter(x=df['Time'], y=df['Lower'], name='Bollinger Lower'))
        else:
            fig.add_trace(go.Candlestick(
                x=df['Time'],
                open=df['Price'],
                high=df['Price'],
                low=df['Price'],
                close=df['Price'],
                name='Candlestick'
            ))
        fig.update_layout(title=coin_name)
        return fig

    fig1 = build_figure(df1, coins[coin1])
    fig2 = build_figure(df2, coins[coin2])

    backtest_output = html.Div([
        html.H3('📊 Backtesting Resultado'),
        html.P(f"{coins[coin1]} - Return: {stats1['Total Return']}%, Trades: {stats1['Trades']}, Wins: {stats1['Wins']}, Losses: {stats1['Losses']}, 🚦 Recomendação: {signal1}"),
        html.P(f"{coins[coin2]} - Return: {stats2['Total Return']}%, Trades: {stats2['Trades']}, Wins: {stats2['Wins']}, Losses: {stats2['Losses']}, 🚦 Recomendação: {signal2}")
    ])

    return fig1, fig2, backtest_output


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
