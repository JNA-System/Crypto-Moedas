# =============================================
# Script: data_fetcher.py
# Projeto: CryptoPrice-Dashboard
# Descrição: Coleta dados detalhados das 10 principais criptomoedas e salva em CSV
# Autor: Nathan Thomaz
# Data de Criação: 27/04/2025
# Versão: 1.0
# =============================================

import requests
import pandas as pd
from datetime import datetime
import os
import glob

# =============================================
# Configurações
# =============================================

MAX_ARQUIVOS_RAW = 5  # Número máximo de arquivos para manter

# =============================================
# Funções
# =============================================

# =============================================
# fetch_crypto_data
# =============================================
def fetch_crypto_data():
    """
    Busca dados de criptomoedas, salva e mantém apenas os 5 arquivos mais recentes.
    """

    # Define URL e parâmetros da API
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }

    # Faz a requisição
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Organiza os dados
    coins = []
    for coin in data:
        coins.append({
            "id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "current_price": coin.get("current_price"),
            "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "total_volume": coin.get("total_volume"),
            "circulating_supply": coin.get("circulating_supply"),
            "ath": coin.get("ath"),
            "atl": coin.get("atl"),
            "last_updated": coin.get("last_updated")
        })

    # Salva os dados
    df = pd.DataFrame(coins)

    today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join("data", "raw", f"crypto_data_{today}.csv")

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)

    # Agora limpa os antigos
    manter_apenas_ultimos_arquivos()

# =============================================
# manter_apenas_ultimos_arquivos
# =============================================
def manter_apenas_ultimos_arquivos():
    """
    Mantém apenas os 5 arquivos mais recentes na pasta data/raw.
    """
    arquivos = sorted(
        glob.glob(os.path.join("data", "raw", "*.csv")),
        key=os.path.getctime,
        reverse=True
    )

    # Se tiver mais que 5 arquivos, apaga os mais antigos
    for arquivo in arquivos[MAX_ARQUIVOS_RAW:]:
        os.remove(arquivo)

# =============================================
# Execução principal
# =============================================

if __name__ == "__main__":
    fetch_crypto_data()
