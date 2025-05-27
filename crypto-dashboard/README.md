# 🪙 Crypto Dashboard - CoinGecko API

Um dashboard simples em Flask que exibe os preços atuais de Bitcoin, Ethereum e Solana em USD e BRL.

## 🚀 Como rodar localmente

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/crypto-dashboard.git
cd crypto-dashboard
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

Acesse no navegador: http://localhost:8080

## 🌐 Deploy na Render (Gratuito)

1. Crie uma conta em https://render.com
2. Clique em **New Web Service**
3. Conecte seu GitHub e selecione este repositório
4. Configure:
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py
5. Clique em **Create Web Service**

A Render criará uma URL pública como:
```
https://crypto-dashboard.onrender.com
```

## 📄 Licença
Este projeto está sob a licença MIT.