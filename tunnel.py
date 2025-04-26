from produit import Produit
from cap import Cap
from floor import Floor
import pandas as pd

class Tunnel(Produit):
    def __init__(self, nominal: str, T: float, fixing: None, strike_floor: float, strike_cap: float, sous_jacent: str, echeancier_simulation: list[pd.Timestamp], echeancier_fixing: list[list[pd.Timestamp, float]], Taux_Fwd: pd.DataFrame, ZC: pd.DataFrame):
        super().__init__(nominal, T, fixing)
        self.__K_cap = strike_cap
        self.__K_floor = strike_floor
        self.__sous_jacent = sous_jacent
        self.__Cap = Cap(self.get_nominal(), self.get_maturite(), self.get_fixing(), strike_cap, sous_jacent, 1,  echeancier_simulation, echeancier_fixing, Taux_Fwd, ZC)
        self.__Floor = Floor(self.get_nominal(), self.get_maturite(), self.get_fixing(), strike_floor, sous_jacent, 1,  echeancier_simulation, echeancier_fixing, Taux_Fwd, ZC)
        self.__price_Cap = None
        self.__price_Floor = None
        self.__price_strat = None

    def Prix(self):
        self.__Cap.CoursSpot()
        self.__Cap.MonteCarlo()
        self.__Cap.Prix()

        self.__Floor.CoursSpot()
        self.__Floor.MonteCarlo()
        self.__Floor.Prix()
        
        self.__price_Cap = self.__Cap.get_price()
        self.__price_Floor = self.__Floor.get_price()

        self.__price_strat = self.__price_Cap - self.__price_Floor

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
    
    def get_price_cap(self):
        return self.__price_Cap
    
    def get_price_floor(self):
        return self.__price_Floor
    
    def get_strike_cap(self) -> float:
        return self.__K_cap
    
    def get_strike_floor(self) -> float:
        return self.__K_floor
    
    def get_sous_jacent(self) -> str:
        return self.__sous_jacent
    
    def get_spot(self) -> float:
        return self.__spot