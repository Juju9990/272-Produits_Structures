from abc import ABC, abstractmethod
from maturite import Maturite


class Produit(ABC):
    def __init__(self, nominal: float, T: float, fixing: str):
        self.__nominal = nominal
        self.__maturite = T
        self.__fixing = fixing

    @abstractmethod
    def MonteCarlo(self):
        """Calcule le prix du produit"""
        pass

    @abstractmethod
    def Payoff(self, spot):
        """Calcule le payoff du produit à maturité"""
        pass
    
    @abstractmethod
    def Prix(self):
        """Retourne le prix de la stratégie/produit"""
        pass

    @abstractmethod
    def Description(self):
        """Retourne une description du produit"""
        pass

    def get_nominal(self) -> float:
        return self.__nominal
    
    def get_maturite(self) -> float:
        return self.__maturite
    
    def get_fixing(self) -> str:
        return self.__fixing