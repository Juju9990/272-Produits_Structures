import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fonctionsannexes import interpoler_smile_de_fichier

class Volatilite:
    def __init__(self, echeancier: list[pd.Timestamp], option: str):
        self.__echeancier = echeancier
        self.__option = option
        self.__smile = None
        self.__smile_Fwd = None
        self.__smile_Fwd_a_matu = None

    def smile(self):
        df_result = pd.DataFrame()
        for date_cible in self.get_echeancier()[1:]:
            try:
                smile_interp = interpoler_smile_de_fichier(date_cible, self.__option)
                df_result = pd.concat([df_result, smile_interp], ignore_index=True)
            except ValueError as e:
                print(f"[{date_cible.date()}] Erreur : {e}")
        self.__smile = df_result.sort_values(by=["expiration", "strike"]).reset_index(drop=True)

    def smile_Fwd_entre_2_simulation(self):               
        self.__smile_Fwd = self.__smile[self.__smile['expiration'] == self.__echeancier[1]]
        self.__smile_Fwd['expiration'] = self.__echeancier[0]
        for i in range (1, len(self.get_echeancier())-1):
            all_strikes = sorted(set(self.__smile[self.__smile['expiration'] == self.__echeancier[i]]['strike']).union(self.__smile[self.__smile['expiration'] == self.__echeancier[i+1]]['strike']))
            smile_1 = self.__smile[self.__smile['expiration'] == self.__echeancier[i]]
            smile_2 = self.__smile[self.__smile['expiration'] == self.__echeancier[i+1]]
            for strike in all_strikes:
                if not strike in set(smile_1['strike']):
                    temp_inf = sorted([s for s in smile_1['strike'] if s < strike])
                    temp_sup = sorted([s for s in smile_1['strike'] if s > strike])
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
                    "expiration": self.__echeancier[i],
                    "strike": strike,
                    "type": self.__option,
                    "Vol_impli": Vol
                    }
                    self.__smile = pd.concat([self.__smile, pd.DataFrame([new_row])], ignore_index=True)
                
                if not strike in set(smile_2['strike']):
                    temp_inf = sorted([s for s in smile_2['strike'] if s < strike])
                    temp_sup = sorted([s for s in smile_2['strike'] if s > strike])
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
                    "expiration": self.__echeancier[i+1],
                    "strike": strike,
                    "type": self.__option,
                    "Vol_impli": Vol
                    }
                    self.__smile = pd.concat([self.__smile, pd.DataFrame([new_row])], ignore_index=True)
                
                self.__smile = self.__smile.sort_values(by=["expiration", "strike"]).reset_index(drop=True)
                Vol_Fwd = (self.__smile[(self.__smile['expiration'] == self.__echeancier[i+1]) & (self.__smile['strike'] == strike)]['Vol_impli'].values[0]**2 * ((self.__echeancier[i+1] - pd.Timestamp.today()).days) / 365 - self.__smile[(self.__smile['expiration'] == self.__echeancier[i]) & (self.__smile['strike'] == strike)]['Vol_impli'].values[0]**2 * ((self.__echeancier[i] - pd.Timestamp.today()).days) / 365) / (((self.__echeancier[i+1] - pd.Timestamp.today()).days) / 365 - ((self.__echeancier[i] - pd.Timestamp.today()).days) / 365)
                Vol_Fwd = np.sqrt(Vol_Fwd)
                new_row = {
                "expiration": self.__echeancier[i],
                "strike": strike,
                "type": self.__option,
                "mark": None,
                "Vol_impli": Vol_Fwd
                }
                self.__smile_Fwd = pd.concat([self.__smile_Fwd, pd.DataFrame([new_row])], ignore_index=True)
        self.__smile_Fwd.rename(columns={"Vol_impli": "Vol_Fwd"}, inplace=True)



    def smile_Fwd_a_matu(self):               
        self.__smile_Fwd_a_matu = self.__smile[(self.__smile['expiration'] == self.__echeancier[-1]) & (self.__smile['type'] == self.__option)]
        self.__smile_Fwd_a_matu['expiration'] = self.__echeancier[0]
        for i in range (1, len(self.get_echeancier())-1):
            all_strikes = sorted(set(self.__smile[(self.__smile['expiration'] == self.__echeancier[i]) & (self.__smile['type'] == self.__option)]['strike']).union(self.__smile[(self.__smile['expiration'] == self.__echeancier[-1]) & (self.__smile['type'] == self.__option)]['strike']))
            smile_1 = self.__smile[(self.__smile['expiration'] == self.__echeancier[i]) & (self.__smile['type'] == self.__option)]
            smile_2 = self.__smile[(self.__smile['expiration'] == self.__echeancier[-1]) & (self.__smile['type'] == self.__option)]
            for strike in all_strikes:
                if not strike in set(smile_1['strike']):
                    temp_inf = sorted([s for s in smile_1['strike'] if s < strike])
                    temp_sup = sorted([s for s in smile_1['strike'] if s > strike])
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
                    "expiration": self.__echeancier[i],
                    "strike": strike,
                    "type": self.__option,
                    "Vol_impli": Vol
                    }
                    self.__smile = pd.concat([self.__smile, pd.DataFrame([new_row])], ignore_index=True)
                
                if not strike in set(smile_2['strike']):
                    temp_inf = sorted([s for s in smile_2['strike'] if s < strike])
                    temp_sup = sorted([s for s in smile_2['strike'] if s > strike])
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
                    "expiration": self.__echeancier[-1],
                    "strike": strike,
                    "type": self.__option,
                    "Vol_impli": Vol
                    }
                    self.__smile = pd.concat([self.__smile, pd.DataFrame([new_row])], ignore_index=True)
                
                self.__smile = self.__smile.sort_values(by=["expiration", "strike"]).reset_index(drop=True)
                Vol_Fwd = (self.__smile[(self.__smile['expiration'] == self.__echeancier[-1]) & (self.__smile['type'] == self.__option) & (self.__smile['strike'] == strike)]['Vol_impli'].values[0]**2 * ((self.__echeancier[-1] - pd.Timestamp.today()).days) / 365 - self.__smile[(self.__smile['expiration'] == self.__echeancier[i]) & (self.__smile['type'] == self.__option) & (self.__smile['strike'] == strike)]['Vol_impli'].values[0]**2 * ((self.__echeancier[i] - pd.Timestamp.today()).days) / 365) / (((self.__echeancier[-1] - pd.Timestamp.today()).days) / 365 - ((self.__echeancier[i] - pd.Timestamp.today()).days) / 365)
                Vol_Fwd = np.sqrt(Vol_Fwd)
                new_row = {
                "expiration": self.__echeancier[i],
                "strike": strike,
                "type": self.__option,
                "mark": None,
                "Vol_impli": Vol_Fwd
                }
                self.__smile_Fwd_a_matu = pd.concat([self.__smile_Fwd_a_matu, pd.DataFrame([new_row])], ignore_index=True)
        self.__smile_Fwd_a_matu.rename(columns={"Vol_impli": "Vol_Fwd"}, inplace=True)
        self.__smile_Fwd_a_matu = self.__smile_Fwd_a_matu.dropna(subset=['Vol_Fwd'])
        self.__smile_Fwd_a_matu =  self.__smile_Fwd_a_matu[(self.__smile_Fwd_a_matu['type'] == self.__option)]


    def afficher_smile(self, date_expiration: pd.Timestamp):
        # Filtrer les données pour la date donnée
        smile = self.__smile[self.__smile['expiration'] == date_expiration].sort_values('strike')

        if smile.empty:
            print(f"Aucune donnée trouvée pour l'expiration {date_expiration.date()}")
            return

        # Tracé
        plt.figure(figsize=(10, 5))
        plt.plot(smile['strike'], smile['Vol_impli'], marker='o', linestyle='-', color='royalblue')
        plt.title(f"Smile de volatilité implicite - Expiration {date_expiration.date()}")
        plt.xlabel("Strike")
        plt.ylabel("Volatilité implicite")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    def afficher_smile_Fwd(self, date_expiration: pd.Timestamp):
        # Filtrer les données pour la date donnée
        smile = self.__smile_Fwd[self.__smile_Fwd['expiration'] == date_expiration].sort_values('strike')

        if smile.empty:
            print(f"Aucune donnée trouvée pour l'expiration {date_expiration.date()}")
            return

        # Tracé
        plt.figure(figsize=(10, 5))
        plt.plot(smile['strike'], smile['Vol_Fwd'], marker='o', linestyle='-', color='royalblue')
        plt.title(f"Smile de volatilité Forward - Expiration {date_expiration.date()}")
        plt.xlabel("Strike")
        plt.ylabel("Volatilité Forward")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def afficher_smile_Fwd_a_matu(self, date_expiration: pd.Timestamp):
        # Filtrer les données pour la date donnée
        smile = self.__smile_Fwd_a_matu[self.__smile_Fwd_a_matu['expiration'] == date_expiration].sort_values('strike')

        if smile.empty:
            print(f"Aucune donnée trouvée pour l'expiration {date_expiration.date()}")
            return

        # Tracé
        plt.figure(figsize=(10, 5))
        plt.plot(smile['strike'], smile['Vol_Fwd'], marker='o', linestyle='-', color='royalblue')
        plt.title(f"Smile de volatilité Forward - Expiration {date_expiration.date()}")
        plt.xlabel("Strike")
        plt.ylabel("Volatilité Forward")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
     
    def get_smile(self) -> pd.DataFrame:
        return self.__smile
    
    def get_smile_Fwd(self) -> pd.DataFrame:
        return self.__smile_Fwd
    
    def get_smile_Fwd_a_matu(self) -> pd.DataFrame:
        return self.__smile_Fwd_a_matu
    
    def get_echeancier(self) -> list[pd.Timestamp]:
        return self.__echeancier
