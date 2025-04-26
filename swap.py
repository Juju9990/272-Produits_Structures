from produit import Produit
from fonctionsannexes import *
import pandas as pd
import numpy as np
from obligation import ObligationTxFixe
from obligation_variable import ObligationTxVariable

class Swap(Produit):
    def __init__(self, nominal: str, T: float, fixing: None, taux_facial: str, echeancier_fixing: list[list[pd.Timestamp, float]], Taux_Fwd: pd.DataFrame, jambe_payeuse: str):
        super().__init__(nominal, T, fixing)
        self.__taux_facial = taux_facial
        self.__echeancier_fixing = echeancier_fixing
        self.__taux_sans_risque = 0.02167
        self.__ObligationTxFixe = ObligationTxFixe(nominal, T, fixing, taux_facial, echeancier_fixing)
        self.__ObligationVariable = ObligationTxVariable(nominal, T, fixing, echeancier_fixing, Taux_Fwd)
        self.__jambe_payeuse = jambe_payeuse
        self.__prix_euro = 0
        self.__prix = 0

    def Prix(self):
        self.__ObligationTxFixe.Prix()
        self.__ObligationVariable.Prix()

        match self.__jambe_payeuse:
            case "Taux payeur fixe":
                self.__prix = self.__ObligationVariable.get_prix() - self.__ObligationTxFixe.get_prix()
                self.__prix_euro = self.__ObligationVariable.get_prix_euro() - self.__ObligationTxFixe.get_prix_euro()
            case "Taux payeur variable":
                self.__prix = self.__ObligationTxFixe.get_prix() - self.__ObligationVariable.get_prix()
                self.__prix_euro = self.__ObligationTxFixe.get_prix_euro() - self.__ObligationVariable.get_prix_euro()

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