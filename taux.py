import numpy as np
import pandas as pd
from datetime import date, datetime,timedelta
from dateutil.relativedelta import relativedelta

class Taux:
    def __init__(self):
        self.__Fwd_2_simu = None
        self.__Fwd = None
        self.__ZC = None

    def Courbe_TauxZC(self, echeancier) -> None:
        df_temp = pd.read_excel("Taux.xlsx")
        df_taux_bis = df_temp.copy()
        df_taux_bis.set_index('Date', inplace=True)

        # Créer une liste pour les taux avec la fréquence demandée
        result = []
 
        current_date = echeancier[0]

        # Boucle jusqu'à la fin des données
        while current_date <= echeancier[-1]:
            date64 = np.datetime64(current_date.date())  
            inter = np.busday_offset(date64, 0, roll='forward')
            if current_date in df_taux_bis.index:
                result.append((current_date, df_taux_bis.loc[current_date, 'TauxZC']))
            else:
                df_sup = df_temp[df_temp['Date'] >= pd.Timestamp(inter)]
                df_inf = df_temp[(df_temp['Date'] < pd.Timestamp(inter))]
                ZC = df_inf['TauxZC'].iloc[-1] + (df_sup['TauxZC'].iloc[0] - df_inf['TauxZC'].iloc[-1]) / (df_sup['Date'].iloc[0] - df_inf['Date'].iloc[-1]).days * (pd.to_datetime(current_date) - df_inf['Date'].iloc[-1]).days
                
                result.append((pd.Timestamp(inter), ZC))
            current_date += relativedelta(months=1)
            
        # Créer un DataFrame final avec les résultats
        self.__ZC = pd.DataFrame(result, columns=['Date', 'TauxZC'])

    def Courbe_TauxZC_Obligation(self, echeancier_fixing: pd.DataFrame, fixing: str) -> None:
        df_temp = pd.read_excel("Taux.xlsx")
        df_taux_bis = df_temp.copy()
        df_taux_bis.set_index('Date', inplace=True)

        # Créer une liste pour les taux avec la fréquence demandée
        result = []
 
        current_date = echeancier_fixing[0][0]

        # Boucle jusqu'à la fin des données
        while current_date <= echeancier_fixing[-1][0] + relativedelta(months=25):
            date64 = np.datetime64(current_date.date())  
            inter = np.busday_offset(date64, 0, roll='forward')
            if inter in df_taux_bis.index:
                result.append((current_date, df_taux_bis.loc[current_date, 'TauxZC']))
            else:
                df_sup = df_temp[df_temp['Date'] >= pd.Timestamp(inter)]
                df_inf = df_temp[(df_temp['Date'] < pd.Timestamp(inter))]
                ZC = df_inf['TauxZC'].iloc[-1] + (df_sup['TauxZC'].iloc[0] - df_inf['TauxZC'].iloc[-1]) / (df_sup['Date'].iloc[0] - df_inf['Date'].iloc[-1]).days * (pd.to_datetime(inter) - df_inf['Date'].iloc[-1]).days
                
                result.append((pd.Timestamp(inter), ZC))
            match fixing:
                case "Trimestriel":
                    current_date += relativedelta(months=3)
                case "Semestriel":
                    current_date += relativedelta(months=6)
                case "Annuel":
                    current_date += relativedelta(months=12)
            
        # Créer un DataFrame final avec les résultats
        self.__ZC = pd.DataFrame(result, columns=['Date', 'TauxZC'])

    def Courbe_TauxFWD_Obligation_entre_2_simu(self):
        result = []
        liste_date = list(self.__ZC['Date'])
        liste_tx = list(self.__ZC['TauxZC'])
        for i in range (len(liste_date)-1):
            if i ==0:
                taux_fwd = liste_tx[i+1]
            else:
                t1 = (pd.Timestamp(liste_date[i]) - pd.Timestamp(liste_date[0])).days / 365
                t2 = (pd.Timestamp(liste_date[i+1]) - pd.Timestamp(liste_date[0])).days / 365
                taux_fwd = ((1 + liste_tx[i+1] * t2) / (1 + liste_tx[i] * t1)) ** (1 / (t2 - t1)) - 1
            result.append((liste_date[i], taux_fwd))
        self.__Fwd_2_simu = pd.DataFrame(result, columns=['Date', 'TauxFWD'])

    def Courbe_TauxFWD_entre_2_simu(self):
        result = []
        liste_date = list(self.__ZC['Date'])
        liste_tx = list(self.__ZC['TauxZC'])
        for i in range (len(liste_date)-1):
            if i ==0:
                taux_fwd = liste_tx[i+1]
            else:
                t1 = (pd.Timestamp(liste_date[i]) - pd.Timestamp(liste_date[0])).days / 365
                t2 = (pd.Timestamp(liste_date[i+1]) - pd.Timestamp(liste_date[0])).days / 365
                taux_fwd = ((1 + liste_tx[i+1] * t2) / (1 + liste_tx[i] * t1)) ** (1 / (t2 - t1)) - 1
            result.append((liste_date[i], taux_fwd))
        self.__Fwd_2_simu = pd.DataFrame(result, columns=['Date', 'TauxFWD'])

    def Courbe_TauxFWD(self):
        result = []
        for date in self.__ZC['Date']:
            if date != self.__ZC['Date'].iloc[0]:
                df_sup = self.__ZC[self.__ZC['Date'] == pd.to_datetime(date)]
                df_inf = self.__ZC[self.__ZC['Date'] < pd.to_datetime(date)]
                taux_fwd = (((1 + df_sup['TauxZC'].iloc[0])**((df_sup['Date'].iloc[0] - df_inf['Date'].iloc[0]).days / 365)) / ((1 + df_inf['TauxZC'].iloc[-1])**((df_inf['Date'].iloc[-1] - df_inf['Date'].iloc[0]).days / 365)))**(1 / ((df_sup['Date'].iloc[0] - df_inf['Date'].iloc[-1]).days/365)) - 1
                
                result.append((date, taux_fwd))
            else:
                result.append((date, self.__ZC['TauxZC'].iloc[0]))

        self.__Fwd = pd.DataFrame(result, columns=['Date', 'TauxFWD'])

    def get_Fwd_simu(self) -> pd.DataFrame:
        return self.__Fwd_2_simu
    
    def get_Fwd(self) -> pd.DataFrame:
        return self.__Fwd
    
    def get_ZC(self) -> pd.DataFrame:
        return self.__ZC
    
    def set_Fwd(self, Fwd) -> None:
        self.__Fwd = Fwd
    
    def set_ZC(self, ZC) -> None:
        self.__ZC = ZC