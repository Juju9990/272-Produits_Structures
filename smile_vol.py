"""
from scipy.stats import norm
from scipy.optimize import brentq
import numpy as np
import os
import pandas as pd
import yfinance as yf

csv_path = os.path.join(os.path.dirname(__file__), "AAPL_one_exp_per_month_full.csv")
df = pd.read_csv(csv_path)
df = df[["expiration", "strike", "bid", "ask"]]
df["mid"] = (df["bid"] + df["ask"]) / 2
df["expiration"] = pd.to_datetime(df["expiration"]) 
df = df[["expiration", "strike", "mid"]].rename(columns={"mid": "C_market"})


def bs_call_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def implied_volatility_call(C_market, S, K, T, r):
    # Fonction objectif : différence entre prix BS et prix marché
    f = lambda sigma: bs_call_price(S, K, T, r, sigma) - C_market
    # Résolution numérique avec brentq dans un intervalle raisonnable
    return brentq(f, 1e-6, 5.0)  # entre 0.000001 et 500%


# Ex : Données marché
S = 196.98  # prix spot
K = 100  # strike
T = 1  # 1 an
r = 0.05  # 5% taux sans risque
C_market = 10  # prix marché du call
vol_imp = implied_volatility_call(C_market, S, K, T, r)
"""

from scipy.stats import norm
from scipy.optimize import brentq
import numpy as np
import os
import pandas as pd
import yfinance as yf

# Chargement des données d'options
csv_path = os.path.join(os.path.dirname(__file__), "AAPL_one_exp_per_month_full.csv")
df = pd.read_csv(csv_path)
df = df[["expiration", "strike", "bid", "ask"]]
df["mid"] = (df["bid"] + df["ask"]) / 200
df["expiration"] = pd.to_datetime(df["expiration"]) 
df = df[["expiration", "strike", "mid"]].rename(columns={"mid": "C_market"})

# Paramètres du modèle
S = 196.98  # prix spot
r = 0.05  # taux sans risque
today = pd.to_datetime("2025-04-17")

# Fonction de pricing Black-Scholes pour call
def bs_call_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

# Calcul de la volatilité implicite
def implied_volatility_call(C_market, S, K, T, r):
    try:
        f = lambda sigma: bs_call_price(S, K, T, r, sigma) - C_market
        return brentq(f, 1e-6, 5.0)
    except (ValueError, RuntimeError):
        return np.nan  # En cas d'erreur numérique, on met NaN

# Calcul de T en années (jour de valorisation : today)
df["T"] = (df["expiration"] - today).dt.days / 365

# Application de la formule à chaque ligne
df["implied_vol"] = df.apply(
    lambda row: implied_volatility_call(row["C_market"], S, row["strike"], row["T"], r),
    axis=1
)

pivot_table = df.pivot_table(index="strike", columns="expiration", values="implied_vol")
#pivot_table.dropna(axis=0, inplace=True)  # Supprimer les colonnes avec NaN


import matplotlib.pyplot as plt

# Pivot propre sans lignes vides
pivot_table = df.pivot_table(index="strike", columns="expiration", values="implied_vol")
pivot_table = pivot_table.dropna(how="all")

# Tracé d'un smile par date d'expiration
plt.figure(figsize=(12, 6))

for expiration in pivot_table.columns:
    plt.plot(pivot_table.index, pivot_table[expiration], label=expiration.strftime("%Y-%m-%d"))

plt.xlabel("Strike")
plt.ylabel("Volatilité implicite")
plt.title("Smiles de volatilité implicite pour AAPL")
plt.legend(title="Expiration")
plt.grid(True)
plt.tight_layout()
plt.show()
