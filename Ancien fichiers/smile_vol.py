# smile_vol.py
import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from scipy.interpolate import RectBivariateSpline
import matplotlib.pyplot as plt
from matplotlib import cm
from io import BytesIO

S = 196.98  # Spot AAPL
r = 0.05    # Taux sans risque


def bs_call_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def bs_put_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def load_and_prepare_data(option_type: str, date_ref: str):
    data = pd.read_csv("AAPL_one_exp_per_month_full.csv", parse_dates=["expiration"])
    today = pd.to_datetime(date_ref)
    data["T"] = (data["expiration"] - today).dt.days / 365
    data = data[data["T"] > 0]

    df = data[data["type"] == option_type].copy()
    df["mid"] = (df["bid"] + df["ask"]) / 2

    def implied_vol(row):
        price, K, T = row["mid"], row["strike"], row["T"]
        try:
            if option_type == "call":
                f = lambda sigma: bs_call_price(S, K, T, r, sigma) - price
            else:
                f = lambda sigma: bs_put_price(S, K, T, r, sigma) - price
            return brentq(f, 1e-6, 5.0)
        except:
            return np.nan

    df["implied_vol"] = df.apply(implied_vol, axis=1)
    return df, today


def display_vol_surface(df, today, option_type="call"):
    pivot = df.pivot_table(index="strike", columns="expiration", values="implied_vol")
    pivot = pivot.dropna(how="any").dropna(axis=1, how="any")
    pivot = pivot.loc[~pivot.index.duplicated()].sort_index()
    pivot = pivot.loc[:, ~pivot.columns.duplicated()].sort_index(axis=1)

    X = pivot.index.values
    Y = np.array([(col - today).days / 365 for col in pivot.columns])
    Z = pivot.values

    interp_func = RectBivariateSpline(X, Y, Z, kx=3, ky=3)
    strike_fine = np.linspace(X.min(), X.max(), 100)
    T_fine = np.linspace(Y.min(), Y.max(), 100)
    X_fine_grid, T_fine_grid = np.meshgrid(strike_fine, T_fine)
    Z_fine = interp_func(strike_fine, T_fine)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X_fine_grid, T_fine_grid, Z_fine, cmap=cm.inferno, edgecolor='k')
    ax.set_title(f"Surface de volatilité implicite - {option_type.upper()}")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Maturité (années)")
    ax.set_zlabel("Vol implicite")
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf