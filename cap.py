from produit import Produit
from fonctionsannexes import *
import pandas as pd
import numpy as np

class Cap(Produit):
    def __init__(self, nominal: str, T: float, fixing: None, strike: float, sous_jacent: str, qty: int, echeancier_simulation: list[pd.Timestamp], echeancier_fixing: list[list[pd.Timestamp, float]], Taux_Fwd: pd.DataFrame, ZC: pd.DataFrame):
        super().__init__(nominal, T, fixing)
        self.__K = strike
        self.__sous_jacent = sous_jacent
        self.__qty = qty
        self.__spot = None
        self.__price = None
        self.__price_strat = None
        self.__echeancier_simulation = echeancier_simulation
        self.__echeancier_fixing = echeancier_fixing
        self.__vol = 0
        self.__Taux_Fwd = Taux_Fwd
        self.__ZC = ZC

    def CoursSpot(self):
        match self.__sous_jacent:
            case "Euribor 3M":
                self.__spot = 0.02386
                df = pd.read_excel("Cours_E3M.xlsx")
                df['log_ret'] = np.log(df['E3M'] / df['E3M'].shift(1))
                vol_journalière = df['log_ret'].std()
                self.__vol = vol_journalière * np.sqrt(252)

    def Payoff(self, ST) -> float:
        """Calcule le payoff du produit à maturité"""
        return max(ST - self.__K, 0)

    def MonteCarlo(self):
        """Calcule le prix du produit"""
        np.random.seed(42)
        MCarlo = 30
        payoff = list()
        for i in range (MCarlo):
            S = list()
            S.append(self.__spot)
            X = np.random.randn(self.__echeancier_fixing[-1][1])
            for j in range (self.__echeancier_fixing[-1][1]-1):
                delta_t = (pd.Timestamp(self.__echeancier_simulation[j+1]) - pd.Timestamp(self.__echeancier_simulation[j])).days / 365
                S.append(S[j] * np.exp((self.__Taux_Fwd[self.__Taux_Fwd['Date'] == self.__echeancier_simulation[j]]['TauxFWD'].values[0] - 1 / 2 * self.__vol ** 2) * delta_t + self.__vol * np.sqrt(delta_t) * X[j]))
            payoff.append(self.Payoff(S[self.__echeancier_fixing[-1][1]-1]))
        self.__price = np.exp(- self.__ZC[self.__ZC['Date'] == self.__echeancier_fixing[-1][0]]['TauxZC'].values[0] * self.get_maturite()) * np.mean(payoff)

    def Prix(self):
        """Retourne le prix de la stratégie/produit"""
        self.__price_strat = self.__qty * self.__price * self.get_nominal()

    def Description(self):
        """Retourne une description du produit"""
        pass
    
    def get_price(self):
        return self.__price_strat 
    
    def get_strike(self) -> float:
        return self.__K
    
    def get_sous_jacent(self) -> str:
        return self.__sous_jacent
    
    def get_quantity(self) -> float:
        return self.__qty
    
    def get_spot(self) -> float:
        return self.__spot