# =============================================
# Script: data_processor.py 
# Projeto: CryptoPrice-Dashboard
# Descrição: Processa e analisa os dados brutos de criptomoedas 
# Autor: Nathan Thomaz
# Data de Atualização: 28/04/2025
# Versão: 2.0
# =============================================

import pandas as pd
import os
from glob import glob
from datetime import datetime

# =============================================
# Funções
# =============================================

def load_latest_data(raw_data_path="data/raw/"):
    list_of_files = glob(os.path.join(raw_data_path, "*.csv"))
    
    if not list_of_files:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado em 'data/raw/'.")

    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    return df


def analyze_data(df):
    # Melhor e pior moeda
    best_coin = df.loc[df['price_change_percentage_24h'].idxmax()]
    worst_coin = df.loc[df['price_change_percentage_24h'].idxmin()]

    # Média geral
    avg_change = df['price_change_percentage_24h'].mean()

    # Top 3 moedas que mais subiram
    top_moedas = df.sort_values(by="price_change_percentage_24h", ascending=False).head(3)

    top1_coin = top_moedas.iloc[0]['name']
    top1_change = top_moedas.iloc[0]['price_change_percentage_24h']

    top2_coin = top_moedas.iloc[1]['name']
    top2_change = top_moedas.iloc[1]['price_change_percentage_24h']

    top3_coin = top_moedas.iloc[2]['name']
    top3_change = top_moedas.iloc[2]['price_change_percentage_24h']

    # Quantidade de moedas que subiram e caíram
    coins_up = (df['price_change_percentage_24h'] > 0).sum()
    coins_down = (df['price_change_percentage_24h'] < 0).sum()

    # Gerar resultado
    result = {
        "best_coin": best_coin['name'],
        "best_change": best_coin['price_change_percentage_24h'],
        "worst_coin": worst_coin['name'],
        "worst_change": worst_coin['price_change_percentage_24h'],
        "average_change": avg_change,
        "top1_coin": top1_coin,
        "top1_change": top1_change,
        "top2_coin": top2_coin,
        "top2_change": top2_change,
        "top3_coin": top3_coin,
        "top3_change": top3_change,
        "coins_up": coins_up,
        "coins_down": coins_down,
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return result


def save_analysis(result, processed_data_path="data/processed/"):
    os.makedirs(processed_data_path, exist_ok=True)
    df_result = pd.DataFrame([result])
    filename = os.path.join(processed_data_path, "crypto_analysis.csv")
    df_result.to_csv(filename, index=False)


# =============================================
# Execução principal
# =============================================

if __name__ == "__main__":
    df = load_latest_data()
    analysis_result = analyze_data(df)
    save_analysis(analysis_result)
