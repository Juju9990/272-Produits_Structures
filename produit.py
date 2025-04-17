from abc import ABC, abstractmethod
from maturite import Maturite


class Produit(ABC):
    def __init__(self, nominal, T, fixing):
        self.nominal = nominal
        self.maturite = Maturite(T=T, fixing=fixing)
        self.Echeancier = self.maturite.CreationEcheancier()
        self.DateMaturite = self.maturite.ExpiryDate()

    @abstractmethod
    def MonteCarlo(self):
        """Calcule le prix du produit"""
        pass

    @abstractmethod
    def Payoff(self, spot):
        """Calcule le payoff du produit à maturité"""
        pass

    @abstractmethod
    def Description(self):
        """Retourne une description du produit"""
        pass
