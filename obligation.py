from produit import Produit
from fonctionsannexes import *
import pandas as pd
import numpy as np

class ObligationTxFixe(Produit):
    def __init__(self, nominal: str, T: float, fixing: None, taux_facial: str, echeancier_fixing: list[list[pd.Timestamp, float]]):
        super().__init__(nominal, T, fixing)
        self.__taux_facial = taux_facial
        self.__echeancier_fixing = echeancier_fixing
        self.__taux_sans_risque = 0.02167
        self.__prix_euro = 0
        self.__prix = 0

    def Prix(self):
        for i in range (1, len(self.__echeancier_fixing)):
            if i != len(self.__echeancier_fixing)-1:
                self.__prix += self.__taux_facial / ((1 + self.__taux_sans_risque)**((pd.Timestamp(self.__echeancier_fixing[i][0]) - pd.Timestamp(self.__echeancier_fixing[0][0])).days / 365))
                self.__prix_euro += self.get_nominal() * self.__taux_facial / ((1 + self.__taux_sans_risque)**((pd.Timestamp(self.__echeancier_fixing[i][0]) - pd.Timestamp(self.__echeancier_fixing[0][0])).days / 365))
            else:
                self.__prix += (1 + self.__taux_facial) / ((1 + self.__taux_sans_risque)**((pd.Timestamp(self.__echeancier_fixing[i][0]) - pd.Timestamp(self.__echeancier_fixing[0][0])).days / 365))
                self.__prix_euro += (self.get_nominal() + self.get_nominal() * self.__taux_facial) / ((1 + self.__taux_sans_risque)**((pd.Timestamp(self.__echeancier_fixing[i][0]) - pd.Timestamp(self.__echeancier_fixing[0][0])).days / 365))
    
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
    