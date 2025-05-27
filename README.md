# 🪙 Crypto Dashboard Pro

Dashboard em tempo real com IA, Candlestick, RSI, MACD, Bollinger e Backtesting.

## 🚀 Como rodar localmente

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/crypto-dashboard-pro.git
cd crypto-dashboard-pro
```

2. Crie um arquivo `.env` com sua chave de API:
```
COINGECKO_API_KEY=CG-rcWHrATZzuhrgSZjFo1o3bwS
```

3. Crie um ambiente virtual (opcional):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Rode o app:
```bash
python app.py
```

Acesse em: http://localhost:8080

## 🌐 Deploy na Render

1. Crie um serviço Web no https://render.com
2. Conecte seu GitHub
3. Configure:
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:server
4. A Render criará uma URL pública.

## 📄 Licença
MIT