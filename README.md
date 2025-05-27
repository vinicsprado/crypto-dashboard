# 🪙 Crypto Dashboard com Dash e IA

Dashboard em tempo real com preço de Bitcoin, Ethereum, Solana, Cardano e Polygon usando API da CoinGecko. IA simples gera sinais de COMPRA ou VENDA.

## 🚀 Como rodar localmente

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/crypto-dashboard-dash.git
cd crypto-dashboard-dash
```

2. Crie um ambiente virtual (opcional):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Rode o app:
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
4. A Render criará uma URL pública como:
```
https://crypto-dashboard-dash.onrender.com
```

## 📄 Licença
MIT