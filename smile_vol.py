import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.stats import norm
from scipy.optimize import brentq
from scipy.interpolate import RectBivariateSpline
from mpl_toolkits.mplot3d import Axes3D

# Chargement des données 
data = pd.read_csv("AAPL_one_exp_per_month_full.csv", parse_dates=["expiration"])

# Filtrage des CALLs uniquement 
df = data[data["type"] == "call"].copy()
df["mid"] = (df["bid"] + df["ask"]) / 2

# Paramètres de marché
today = pd.to_datetime("2025-04-17")
S = 196.98
r = 0.05

# Maturité (en années)
df["T"] = (pd.to_datetime(df["expiration"]) - today).dt.days / 365
df = df[df["T"] > 0]  # éliminer options expirées

# Black-Scholes inversé
def bs_call_price(S, K, T, r, sigma):
    if T <= 0 or sigma <= 0:
        return max(S - K, 0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def implied_volatility_call(C_market, S, K, T, r):
    try:
        f = lambda sigma: bs_call_price(S, K, T, r, sigma) - C_market
        return brentq(f, 1e-6, 5.0)
    except Exception:
        return np.nan

df["implied_vol"] = df.apply(
    lambda row: implied_volatility_call(row["mid"], S, row["strike"], row["T"], r),
    axis=1
)

# Construction de la surface pivotée
pivot = df.pivot_table(index="strike", columns="expiration", values="implied_vol")
pivot = pivot.dropna(how="any").dropna(axis=1, how="any")
pivot = pivot.loc[~pivot.index.duplicated()].sort_index()
pivot = pivot.loc[:, ~pivot.columns.duplicated()].sort_index(axis=1)

# Grilles pour interpolation 
X = pivot.index.values  # strikes
Y = np.array([(col - today).days / 365 for col in pivot.columns])  # maturité (en années)
Z = pivot.values  # shape: (len(X), len(Y))
assert Z.shape == (len(X), len(Y)), "Dimensions X/Y et Z incompatibles"

# Interpolation bicubique
interp_func = RectBivariateSpline(X, Y, Z, kx=3, ky=3)

# Grille fine (100 x 100) pour interpolation complète
strike_fine = np.linspace(X.min(), X.max(), 100)
T_fine = np.linspace(Y.min(), Y.max(), 100)

# Clipping des bornes pour éviter erreur bispev:10
strike_fine_clipped = np.clip(strike_fine, X.min(), X.max())
T_fine_clipped = np.clip(T_fine, Y.min(), Y.max())

X_fine_grid, T_fine_grid = np.meshgrid(strike_fine_clipped, T_fine_clipped)
Z_fine = interp_func(strike_fine_clipped, T_fine_clipped)

# Tracé de la surface 3D interpolée
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X_fine_grid, T_fine_grid, Z_fine, cmap=cm.inferno, edgecolor='k', alpha=0.9)
ax.set_title("Surface de volatilité implicite interpolée (cubique)")
ax.set_xlabel("Strike")
ax.set_ylabel("Maturité (années)")
ax.set_zlabel("Volatilité implicite")
plt.tight_layout()
plt.show()

# Exemple d'interpolation
strike_test = 115
T_test = 0.3
vol_test = interp_func(strike_test, T_test)[0][0]
print(f"Volatilité implicite interpolée pour strike={strike_test}, T={T_test} ans : {vol_test:.4f}")

df_surface = pd.DataFrame(Z_fine, index=T_fine_clipped, columns=strike_fine_clipped)
df_surface.index.name = "Maturity (years)"
df_surface.columns.name = "Strike"
df_surface.head()
