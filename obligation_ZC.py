from produit import Produit
from fonctionsannexes import *
import pandas as pd
import numpy as np

class ObligationZC(Produit):
    def __init__(self, nominal: str, T: float, fixing: None, taux_facial: float, echeancier_fixing: list[list[pd.Timestamp, float]]):
        super().__init__(nominal, T, fixing)
        self.__echeancier_fixing = echeancier_fixing
        self.__taux_facial = taux_facial
        self.__taux_sans_risque = 0.02167
        self.__prix_euro = 0
        self.__prix = 0

    def Prix(self):
        self.__prix +=  (1 + self.__taux_facial) / ((1 + self.__taux_sans_risque)**self.get_maturite())
        self.__prix_euro += self.get_nominal() * (1 + self.__taux_facial) / ((1 + self.__taux_sans_risque)**self.get_maturite())
    
    def Payoff(self, ST) -> float:
        """Calcule le payoff du produit à maturité"""
        pass

    def MonteCarlo(self):
        """Calcule le prix du produit"""
        pass

    def Description(self):
        """Retourne une description du produit"""
        pass

    def get_prix(self) -> float:
        return self.__prix
    
    def get_prix_euro(self) -> float:
        return self.__prix_euro
    
    def get_taux_facial(self) -> float:
        return self.__taux_facial
    
    def get_echeancier_fixing(self) -> list[pd.Timestamp]:
        return self.__echeancier_fixing
    