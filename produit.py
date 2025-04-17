from abc import ABC, abstractmethod


class Produit(ABC):
    def __init__(self, nominal, maturite, quantite):
        self.nominal = nominal
        self.maturite = maturite

    @abstractmethod
    def prix(self):
        """Calcule le prix du produit"""
        pass

    @abstractmethod
    def payoff(self, spot):
        """Calcule le payoff du produit à maturité"""
        pass

    @abstractmethod
    def description(self):
        """Retourne une description du produit"""
        pass
