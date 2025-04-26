from scipy.stats import norm
from scipy.optimize import brentq
import numpy as np
import pandas as pd
from datetime import date, datetime
from scipy.optimize import minimize
from dateutil.relativedelta import relativedelta
import yfinance as yf
from taux import Taux

# Fonction de calcul du prix d'option Black-Scholes
def bs_price(S, K, T, r, sigma, option_type):
    d1 = (np.log(S/K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Fonction de volatilité implicite
def implied_volatility(C_market, S, K, T, r, option_type):
    def objective(sigma):
        price = bs_price(S, K, T, r, sigma, option_type)
        return price - C_market

    if (objective(1e-6) > 0 and objective(3.0) > 0) or (objective(1e-6) < 0 and objective(3.0) < 0):
        return "NaN"
    else:
        return brentq(objective, 1e-6, 3.0)
    


def generer_smile(sous_jacent: str) -> pd.DataFrame:
    match sous_jacent:
        case  "Apple":
            target_date = '2025-04-17'
            ticker = yf.Ticker("AAPL")
            historical_data = ticker.history(start=target_date, end='2025-04-18')
            spot = historical_data.loc[target_date]['Close']

            df = pd.read_excel("Vol_Apple.xlsx")
            df["expiration"] = pd.to_datetime(df["expiration"])
            df = df[df["expiration"] > pd.Timestamp.today()]
            df = df[["expiration", "strike", "type", "mark"]]
            df["Vol_impli"] = None

    for index, row in df.iterrows():
        date_expiration = row["expiration"]
        K = row["strike"]
        price_market = row["mark"]
        Option_type = row["type"]
        T = (date_expiration - pd.Timestamp.today()).days / 365

        tx = Taux()
        tx.Courbe_TauxZC([date_expiration])
        ZC = tx.get_ZC()
        ZC = ZC.loc[ZC["Date"] == date_expiration, "TauxZC"].iloc[0]

        Vol = implied_volatility(price_market, spot, K, T, ZC, Option_type)
        if Vol == "NaN":
            df = df.drop(index)
        else:
            df.at[index, "Vol_impli"] = Vol

    # Sauvegarde du fichier, remplacement automatique s’il existe
    df.to_csv("smile.csv", sep=';', index=False)

    return df

def interpoler_smile_de_fichier(date_cible: pd.Timestamp, option :str) -> pd.DataFrame:
    # 1. Lire le fichier CSV
    df = pd.read_csv("smile.csv", sep=";")
    df['expiration'] = pd.to_datetime(df['expiration'])

    # 2. Identifier les deux dates encadrantes autour de la date cible
    dates = sorted(df['expiration'].unique())
    dates_inf = [d for d in dates if d < date_cible]
    dates_sup = [d for d in dates if d > date_cible]

    if not dates_inf or not dates_sup:
        raise ValueError("La date cible doit être strictement entre deux dates de smiles existants.")

    # Trouver les dates d'expiration avant et après la date cible
    date1 = max(dates_inf)
    date2 = min(dates_sup)

    # 3. Extraire les deux smiles des dates encadrantes
    smile_1 = df[(df['expiration'] == date1) & (df['type'] == option)].sort_values('strike')
    smile_2 = df[(df['expiration'] == date2) & (df['type'] == option)].sort_values('strike')

    # 4. Trouver l'ensemble complet des strikes (uniquement les strikes existants dans les deux smiles)
    all_strikes = sorted(set(smile_1['strike']).union(smile_2['strike']))
    df_inf = sorted(smile_1['strike'])
    df_sup = sorted(smile_2['strike'])

    for strike in all_strikes:
        if strike not in df_inf:
            temp_inf = sorted([s for s in df_inf if s < strike])
            temp_sup = sorted([s for s in df_inf if s > strike])

            if not temp_inf:
                strike_inf = temp_sup[0]
                strike_sup = temp_sup[1]
                Vol = smile_1[smile_1['strike'] == strike_inf]['Vol_impli'].values[0] + (smile_1[smile_1['strike'] == strike_inf]['Vol_impli'].values[0] - smile_1[smile_1['strike'] == strike_sup]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike_inf - strike)
            elif not temp_sup:
                strike_inf = temp_inf[-2]
                strike_sup = temp_inf[-1]
                Vol = smile_1[smile_1['strike'] == strike_sup]['Vol_impli'].values[0] + (smile_1[smile_1['strike'] == strike_sup]['Vol_impli'].values[0] - smile_1[smile_1['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_sup)
            else:
                strike_inf = max(temp_inf)
                strike_sup = min(temp_sup)
                Vol = smile_1[smile_1['strike'] == strike_inf]['Vol_impli'].values[0] + (smile_1[smile_1['strike'] == strike_sup]['Vol_impli'].values[0] - smile_1[smile_1['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_inf)
            new_row = {
                "expiration": date1,
                "strike": strike,
                "type": option, 
                "mark": None,
                "Vol_impli": Vol
            }
            smile_1 = pd.concat([smile_1, pd.DataFrame([new_row])], ignore_index=True)
        
        if strike not in df_sup:
            temp_inf = sorted([s for s in df_sup if s < strike])
            temp_sup = sorted([s for s in df_sup if s > strike])

            if not temp_inf:
                strike_inf = temp_sup[0]
                strike_sup = temp_sup[1]
                Vol = smile_2[smile_2['strike'] == strike_inf]['Vol_impli'].values[0] + (smile_2[smile_2['strike'] == strike_inf]['Vol_impli'].values[0] - smile_2[smile_2['strike'] == strike_sup]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike_inf - strike)
            elif not temp_sup:
                strike_inf = temp_inf[-2]
                strike_sup = temp_inf[-1]
                Vol = smile_2[smile_2['strike'] == strike_sup]['Vol_impli'].values[0] + (smile_2[smile_2['strike'] == strike_sup]['Vol_impli'].values[0] - smile_2[smile_2['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_sup)
            else:
                strike_inf = max(temp_inf)
                strike_sup = min(temp_sup)
                Vol = smile_2[smile_2['strike'] == strike_inf]['Vol_impli'].values[0] + (smile_2[smile_2['strike'] == strike_sup]['Vol_impli'].values[0] - smile_2[smile_2['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_inf)
            new_row = {
                "expiration": date2,
                "strike": strike,
                "type": option, 
                "mark": None,
                "Vol_impli": Vol
            }
            smile_2 = pd.concat([smile_2, pd.DataFrame([new_row])], ignore_index=True)

    smile_1 = smile_1[smile_1['type'] == option].sort_values('strike')
    smile_2 = smile_2[smile_2['type'] == option].sort_values('strike')

    #print(smile_1)
    #print(smile_2)

    # 6. Interpolation quadratique sur la variance
    t1 = (date1 - pd.Timestamp.today()).days
    t2 = (date2 - pd.Timestamp.today()).days
    t = (date_cible - pd.Timestamp.today()).days

    if t1 == t2 or t == t1 or t == t2:
        raise ValueError("Les dates doivent être distinctes pour interpolation.")

    vol_interp = []
    for strike in all_strikes:
        v1 = smile_1[(smile_1['strike'] == strike) & (smile_1['type'] == option)]['Vol_impli'].values[0]
        v2 = smile_2[(smile_2['strike'] == strike) & (smile_2['type'] == option)]['Vol_impli'].values[0]

        # Calcul des variances
        var1 = v1**2 * t1
        var2 = v2**2 * t2
        var_target = var1 + (var2 - var1) * (t - t1) / (t2 - t1)
        
        # Calcul de la volatilité à la date cible
        vol_target = np.sqrt(var_target / t)

        vol_interp.append((date_cible, strike, option, vol_target))

    return pd.DataFrame(vol_interp, columns=["expiration", "strike", "type", "Vol_impli"])



def vol_local_square(K: float, date: pd.Timestamp, echeancier_simulation: list[pd.Timestamp], smile: pd.DataFrame, option: str, div: float, maturite: float) -> float:
    
    df_1 = smile[(smile["expiration"] == date) & (smile["type"] == option)]
    print(df_1)
    all_strikes = [K-1, K, K+1]
    for strike in all_strikes:
        if strike not in set(df_1['strike']):
            temp_inf = [m for m in sorted(set(df_1['strike'])) if m < strike]
            temp_sup = [m for m in sorted(set(df_1['strike'])) if m > strike]
            if not temp_inf:
                strike_inf = temp_sup[0]
                strike_sup = temp_sup[1]
                Vol = df_1[df_1['strike'] == strike_inf]['Vol_impli'].values[0] + (df_1[df_1['strike'] == strike_inf]['Vol_impli'].values[0] - df_1[df_1['strike'] == strike_sup]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike_inf - strike)
            elif not temp_sup:
                strike_inf = temp_inf[-2]
                strike_sup = temp_inf[-1]
                Vol = df_1[df_1['strike'] == strike_sup]['Vol_impli'].values[0] + (df_1[df_1['strike'] == strike_sup]['Vol_impli'].values[0] - df_1[df_1['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_sup)
            else:
                strike_inf = max(temp_inf)
                strike_sup = min(temp_sup)
                Vol = df_1[df_1['strike'] == strike_inf]['Vol_impli'].values[0] + (df_1[df_1['strike'] == strike_sup]['Vol_impli'].values[0] - df_1[df_1['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_inf)
            new_row = {
                "expiration": date,
                "strike": strike,
                "type": option,
                "mark": None,
                "Vol_impli": Vol,
                }
            smile = pd.concat([smile, pd.DataFrame([new_row])], ignore_index=True)

    derive_premiere_strike = (smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K+1)]['Vol_impli'].values[0] - smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K-1)]['Vol_impli'].values[0]) / 2
    derive_seconde_strike = (smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K+1)]['Vol_impli'].values[0] + smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K-1)]['Vol_impli'].values[0] - 2 * smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K)]['Vol_impli'].values[0])

    for i in range (len(echeancier_simulation)):
        if echeancier_simulation[i] == date:
            break

    if i != len(echeancier_simulation)-1:
        df_bis = smile[(smile["expiration"] == echeancier_simulation[i+1]) & (smile["type"] == option)]
        if K not in set(df_bis['strike']):
            temp_inf = sorted([m for m in df_bis['strike'] if m < K])
            temp_sup = sorted([m for m in df_bis['strike'] if m > K])
            if not temp_inf:
                strike_inf = temp_sup[0]
                strike_sup = temp_sup[1]
                Vol = df_bis[df_bis['strike'] == strike_inf]['Vol_impli'].values[0] + (df_bis[df_bis['strike'] == strike_inf]['Vol_impli'].values[0] - df_bis[df_bis['strike'] == strike_sup]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike_inf - strike) 
            elif not temp_sup:
                strike_inf = temp_inf[-2]
                strike_sup = temp_inf[-1]
                Vol = df_bis[df_bis['strike'] == strike_sup]['Vol_impli'].values[0] + (df_bis[df_bis['strike'] == strike_sup]['Vol_impli'].values[0] - df_bis[df_bis['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_sup)
            else:
                strike_inf = max(temp_inf)
                strike_sup = min(temp_sup)
                Vol = df_bis[df_bis['strike'] == strike_inf]['Vol_impli'].values[0] + (df_bis[df_bis['strike'] == strike_sup]['Vol_impli'].values[0] - df_bis[df_bis['strike'] == strike_inf]['Vol_impli'].values[0]) / (strike_sup - strike_inf) * (strike - strike_inf)
            new_row = {
                "expiration": echeancier_simulation[i+1],
                "strike": K,
                "type": option,
                "mark": None,
                "Vol_impli": Vol,
                }
            smile = pd.concat([smile, pd.DataFrame([new_row])], ignore_index=True)
        delta_t = (pd.Timestamp(echeancier_simulation[i+1]) - pd.Timestamp(date)).days / 365
        derive_premiere_maturite = (smile[(smile["expiration"] == echeancier_simulation[i+1]) & (smile["type"] == option) & (smile["strike"] == K)]['Vol_impli'].values[0] - smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile["strike"] == K)]['Vol_impli'].values[0]) / delta_t
    else:
        print("La volatilité locale à maturité ne sert à rien. Veuillez choisir une autre date !")

    tx = Taux()
    tx.Courbe_TauxZC([date])
    ZC = tx.get_ZC()
    ZC = ZC.loc[ZC["Date"] == date, "TauxZC"].iloc[0]
    
    Vol_impl = smile[(smile['expiration'] == date) & (smile['type'] == option) & (smile['strike'] == K)]['Vol_impli'].values[0]
    #T = (pd.Timestamp(echeancier_simulation[-1]) - pd.Timestamp(date)).days / 365
    T = maturite
    numerateur = Vol_impl**2 + 2 * Vol_impl * T * (derive_premiere_maturite + (ZC - div) * K * derive_premiere_strike)
    denominateur = (1 + K * div * derive_premiere_strike * np.sqrt(T))**2 + Vol_impl * K**2 * T * (derive_seconde_strike - div * derive_premiere_strike**2 * np.sqrt(T))
    return np.abs(numerateur / denominateur)


def vol_local_a_matu(K: float, date: pd.Timestamp, echeancier_simulation: list[pd.Timestamp], smile: pd.DataFrame, option: str, div: float, maturite: float) -> float:
    
    df_1 = smile[(smile["expiration"] == date) & (smile["type"] == option)]

    all_strikes = [K-1, K, K+1]
    for strike in all_strikes:
        if strike not in set(df_1['strike']):
            temp_inf = [m for m in sorted(set(df_1['strike'])) if m < strike]
            temp_sup = [m for m in sorted(set(df_1['strike'])) if m > strike]
            if not temp_inf:
                strike_inf = temp_sup[0]
                strike_sup = temp_sup[1]
                Vol = df_1[df_1['strike'] == strike_inf]['Vol_Fwd'].values[0] + (df_1[df_1['strike'] == strike_inf]['Vol_Fwd'].values[0] - df_1[df_1['strike'] == strike_sup]['Vol_Fwd'].values[0]) / (strike_sup - strike_inf) * (strike_inf - strike)
            elif not temp_sup:
                strike_inf = temp_inf[-2]
                strike_sup = temp_inf[-1]
                Vol = df_1[df_1['strike'] == strike_sup]['Vol_Fwd'].values[0] + (df_1[df_1['strike'] == strike_sup]['Vol_Fwd'].values[0] - df_1[df_1['strike'] == strike_inf]['Vol_Fwd'].values[0]) / (strike_sup - strike_inf) * (strike - strike_sup)
            else:
                strike_inf = max(temp_inf)
                strike_sup = min(temp_sup)
                Vol = df_1[df_1['strike'] == strike_inf]['Vol_Fwd'].values[0] + (df_1[df_1['strike'] == strike_sup]['Vol_Fwd'].values[0] - df_1[df_1['strike'] == strike_inf]['Vol_Fwd'].values[0]) / (strike_sup - strike_inf) * (strike - strike_inf)
            new_row = {
                "expiration": date,
                "strike": strike,
                "type": option,
                "mark": None,
                "Vol_Fwd": Vol,
                }
            smile = pd.concat([smile, pd.DataFrame([new_row])], ignore_index=True)

    derive_premiere_strike = (smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K+1)]['Vol_Fwd'].values[0] - smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K-1)]['Vol_Fwd'].values[0]) / 2
    derive_seconde_strike = (smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K+1)]['Vol_Fwd'].values[0] + smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K-1)]['Vol_Fwd'].values[0] - 2 * smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile['strike'] == K)]['Vol_Fwd'].values[0])

    for i in range (len(echeancier_simulation)):
        if echeancier_simulation[i] == date:
            break
    
    if i != len(echeancier_simulation)-1:
        df_bis = smile[(smile["expiration"] == echeancier_simulation[i+1]) & (smile["type"] == option)]
        if K not in set(df_bis['strike']):
            temp_inf = sorted([m for m in df_bis['strike'] if m < K])
            temp_sup = sorted([m for m in df_bis['strike'] if m > K])
            if not temp_inf:
                strike_inf = temp_sup[0]
                strike_sup = temp_sup[1]
                Vol = df_bis[df_bis['strike'] == strike_inf]['Vol_Fwd'].values[0] + (df_bis[df_bis['strike'] == strike_inf]['Vol_Fwd'].values[0] - df_bis[df_bis['strike'] == strike_sup]['Vol_Fwd'].values[0]) / (strike_sup - strike_inf) * (strike_inf - strike) 
            elif not temp_sup:
                strike_inf = temp_inf[-2]
                strike_sup = temp_inf[-1]
                Vol = df_bis[df_bis['strike'] == strike_sup]['Vol_Fwd'].values[0] + (df_bis[df_bis['strike'] == strike_sup]['Vol_Fwd'].values[0] - df_bis[df_bis['strike'] == strike_inf]['Vol_Fwd'].values[0]) / (strike_sup - strike_inf) * (strike - strike_sup)
            else:
                strike_inf = max(temp_inf)
                strike_sup = min(temp_sup)
                Vol = df_bis[df_bis['strike'] == strike_inf]['Vol_Fwd'].values[0] + (df_bis[df_bis['strike'] == strike_sup]['Vol_Fwd'].values[0] - df_bis[df_bis['strike'] == strike_inf]['Vol_Fwd'].values[0]) / (strike_sup - strike_inf) * (strike - strike_inf)
            new_row = {
                "expiration": echeancier_simulation[i+1],
                "strike": K,
                "type": option,
                "mark": None,
                "Vol_Fwd": Vol,
                }
            smile = pd.concat([smile, pd.DataFrame([new_row])], ignore_index=True)
        delta_t = (pd.Timestamp(echeancier_simulation[i+1]) - pd.Timestamp(date)).days / 365
        derive_premiere_maturite = (smile[(smile["expiration"] == echeancier_simulation[i+1]) & (smile["type"] == option) & (smile["strike"] == K)]['Vol_Fwd'].values[0] - smile[(smile["expiration"] == date) & (smile["type"] == option) & (smile["strike"] == K)]['Vol_Fwd'].values[0]) / delta_t
    else:
        print("La volatilité locale à maturité ne sert à rien. Veuillez choisir une autre date !")

    tx = Taux()
    tx.Courbe_TauxZC([date])
    ZC = tx.get_ZC()
    ZC = ZC.loc[ZC["Date"] == date, "TauxZC"].iloc[0]
    
    Vol_impl = smile[(smile['expiration'] == date) & (smile['type'] == option) & (smile['strike'] == K)]['Vol_Fwd'].values[0]
    T = (pd.Timestamp(echeancier_simulation[-1]) - pd.Timestamp(date)).days / 365

    numerateur = Vol_impl**2 + 2 * Vol_impl * T * (derive_premiere_maturite + (ZC - div) * K * derive_premiere_strike)
    denominateur = (1 + K * div * derive_premiere_strike * np.sqrt(T))**2 + Vol_impl * K**2 * T * (derive_seconde_strike - div * derive_premiere_strike**2 * np.sqrt(T))
    #return np.abs(numerateur / denominateur)
    return Vol_impl

# === Fonction de pricing Heston simplifiée ===
def price_heston_call_cos(S, K, T, r, v0, theta, kappa, sigma, rho, N=128):
    # Cette fonction peut être remplacée par un pricer Heston COS complet ou une version de Heston semi-analytique
    # Ici on met un placeholder avec Black-Scholes juste pour calibration structure
    d1 = (np.log(S/K) + (r + v0/2) * T) / (np.sqrt(v0) * np.sqrt(T))
    d2 = d1 - np.sqrt(v0) * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)

# === Récupérer le taux ZC pour une maturité donnée ===
def get_rate(T, ZC):
    ZC['T'] = (pd.to_datetime(ZC['Date']) - pd.Timestamp.today()).dt.days / 365
    idx = (ZC['T'] - T).abs().idxmin()
    return ZC.loc[idx, 'TauxZC']

# === Fonction objectif pour la calibration ===
def objective(params, df, spot, ZC):
    v0, theta, kappa, sigma, rho = params
    error = 0

    for _, row in df.iterrows():
        T = (pd.to_datetime(row['expiration']) - pd.Timestamp.today()).days / 365
        if T <= 0: continue
        K = row['strike']
        market_price = row['mark']
        r = get_rate(T, ZC)

        model_price = price_heston_call_cos(spot, K, T, r, v0, theta, kappa, sigma, rho)

        error += (model_price - market_price)**2

    return error

# === Fonction principale de calibration ===
def CalibrationHeston(sous_jacent, ZC):
    match sous_jacent:
        case  "Apple":
            target_date = '2025-04-17'
            ticker = yf.Ticker("AAPL")
            historical_data = ticker.history(start=target_date, end='2025-04-18')
            spot = historical_data.loc[target_date]['Close']

            df = pd.read_excel("Vol_Apple.xlsx")
            df["expiration"] = pd.to_datetime(df["expiration"])
            df = df[["expiration", "strike", "type", "mark"]]
    df = df[(df['type'] == 'call')]

    # Bornes raisonnables pour chaque paramètre
    bounds = [
        (0.0001, 1.0),  # v0
        (0.0001, 1.0),  # theta
        (0.01, 10.0),   # kappa
        (0.01, 1.0),    # sigma
        (-0.999, 0.999) # rho
    ]

    # Paramètres initiaux devinés
    x0 = [0.04, 0.04, 1.0, 0.3, -0.7]

    result = minimize(objective, x0, args=(df, spot, ZC), bounds=bounds, method='L-BFGS-B')

    return {
        "v0": result.x[0],
        "theta": result.x[1],
        "kappa": result.x[2],
        "sigma": result.x[3],
        "rho": result.x[4],
        "erreur": result.fun
    }


