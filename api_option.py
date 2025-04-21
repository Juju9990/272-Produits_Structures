import requests
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

API_KEY = "J0J68UE2RS8CBE0R"
SYMBOL = "AAPL"

# RECUPERER TOUTES LES OPTIONS DISPO

# Construire l’URL et les paramètres avec datatype=csv
url = "https://www.alphavantage.co/query"
params = {
    "function": "HISTORICAL_OPTIONS",  # Historical Options Trending :contentReference[oaicite:0]{index=0}
    "symbol": SYMBOL,
    "datatype": "csv",  # demande la sortie au format CSV
    "apikey": API_KEY,
}

# Appel API
response = requests.get(url, params=params)
response.raise_for_status()

# Sauvegarde brute du CSV retourné
csv_filename = f"{SYMBOL}_options_chain.csv"
with open(csv_filename, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"Chaîne d'options exportée dans : {csv_filename}")
