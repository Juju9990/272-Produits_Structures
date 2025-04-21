from scipy.stats import norm
from scipy.optimize import brentq
import numpy as np


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
S = 100  # prix spot
K = 100  # strike
T = 1  # 1 an
r = 0.05  # 5% taux sans risque
C_market = 10  # prix marché du call
vol_imp = implied_volatility_call(C_market, S, K, T, r)

print(f"Volatilité implicite : {vol_imp:.4%}")
