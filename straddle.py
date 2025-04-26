from produit import Produit
from call import Call
from put import Put
from fonctionsannexes import *
import pandas as pd
import yfinance as yf

class Straddle(Produit):
    def __init__(self, nominal: str, T: float, fixing: None, sous_jacent: str, echeancier_simulation: list[pd.Timestamp], echeancier_fixing: list[list[pd.Timestamp, float]], smile_call: pd.DataFrame, smile_put: pd.DataFrame, Taux_Fwd: pd.DataFrame, ZC: pd.DataFrame):
        super().__init__(nominal, T, fixing)
        self.__sous_jacent = sous_jacent
        target_date = '2025-04-17'
        ticker = yf.Ticker("AAPL")
        historical_data = ticker.history(start=target_date, end='2025-04-18')
        self.__spot = historical_data.loc[target_date]['Close']
        self.__Call = Call(self.get_nominal(), self.get_maturite(), self.get_fixing(), self.__spot, sous_jacent, 1,  echeancier_simulation, echeancier_fixing, smile_call, Taux_Fwd, ZC)
        self.__Put = Put(self.get_nominal(), self.get_maturite(), self.get_fixing(), self.__spot, sous_jacent, 1,  echeancier_simulation, echeancier_fixing, smile_put, Taux_Fwd, ZC)
        self.__price_Call = None
        self.__price_Put = None
        self.__price_strat = None
    
    
    def Prix(self):
        self.__Call.CoursSpot()
        self.__Call.MonteCarlo()
        self.__Call.Prix()

        self.__Put.CoursSpot()
        self.__Put.MonteCarlo()
        self.__Put.Prix()
        
        self.__price_Call = self.__Call.get_price()
        self.__price_Put = self.__Put.get_price()

        self.__price_strat = self.__price_Call + self.__price_Put

    def MonteCarlo(self):
        """Calcule le prix du produit"""
        pass

    def Payoff(self, spot):
        """Calcule le payoff du produit à maturité"""
        pass

    def Description(self):
        """Retourne une description du produit"""
        pass

    def get_price_strat(self):
        return self.__price_strat
    
    def get_price_call(self):
        return self.__price_Call
    
    def get_price_put(self):
        return self.__price_Put
    
    def get_sous_jacent(self) -> str:
        return self.__sous_jacent
    
    def get_quantity(self) -> float:
        return self.__qty
    
    def get_spot(self) -> float:
        return self.__spot