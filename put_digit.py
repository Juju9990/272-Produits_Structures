from abc import abstractmethod
from produit import Produit
from fonctionsannexes import *
import pandas as pd
import numpy as np
import yfinance as yf


class Put_Digit(Produit):
    def __init__(
        self,
        nominal: str,
        T: float,
        fixing: None,
        strike: float,
        sous_jacent: str,
        qty: int,
        coupon: float,
        echeancier_simulation: list[pd.Timestamp],
        echeancier_fixing: list[list[pd.Timestamp, float]],
        smile: pd.DataFrame,
        Taux_Fwd: pd.DataFrame,
        ZC: pd.DataFrame,
    ):
        super().__init__(nominal, T, fixing)
        self.__K = strike
        self.__sous_jacent = sous_jacent
        self.__qty = qty
        self.__coupon = coupon
        self.__spot = None
        self.__div = None
        self.__price = None
        self.__price_strat = None
        self.__echeancier_simulation = echeancier_simulation
        self.__echeancier_fixing = echeancier_fixing
        self.__smile = smile
        self.__Taux_Fwd = Taux_Fwd
        self.__ZC = ZC

    def CoursSpot(self):
        match self.__sous_jacent:
            case "Apple":
                target_date = "2025-04-17"
                ticker = yf.Ticker("AAPL")
                historical_data = ticker.history(start=target_date, end="2025-04-18")
                self.__spot = historical_data.loc[target_date]["Close"]
                self.__div = 0.04

    def Payoff(self, ST) -> float:
        """Calcule le payoff du produit à maturité"""
        if ST <= self.__K:
            return self.__coupon * self.get_nominal()
        else:
            return 0

    def MonteCarlo(self):
        """Calcule le prix du produit"""
        np.random.seed(42)
        MCarlo = 30
        payoff = list()
        for i in range(MCarlo):
            S = list()
            S.append(self.__spot)
            X = np.random.randn(self.__echeancier_fixing[-1][1])
            for j in range(self.__echeancier_fixing[-1][1] - 1):
                delta_t = (
                    pd.Timestamp(self.__echeancier_simulation[j + 1])
                    - pd.Timestamp(self.__echeancier_simulation[j])
                ).days / 365
                vol_local = vol_local_a_matu(
                    S[j],
                    self.__echeancier_simulation[j],
                    self.__echeancier_simulation,
                    self.__smile,
                    "put",
                    self.__div,
                    self.get_maturite(),
                )
                S.append(
                    np.exp(
                        np.log(S[j])
                        + (
                            self.__Taux_Fwd[
                                self.__Taux_Fwd["Date"]
                                == self.__echeancier_simulation[j]
                            ]["TauxFWD"].values[0]
                            - vol_local / 2
                        )
                        * delta_t
                        + vol_local * np.sqrt(delta_t) * X[j]
                    )
                )
            if S[self.__echeancier_fixing[-1][1] - 1] < 2000:
                payoff.append(self.Payoff(S[self.__echeancier_fixing[-1][1] - 1]))
        self.__price = np.exp(
            -self.__ZC[self.__ZC["Date"] == self.__echeancier_fixing[-1][0]][
                "TauxZC"
            ].values[0]
            * self.get_maturite()
        ) * np.mean(payoff)

    def Prix(self):
        """Retourne le prix de la stratégie/produit"""
        self.__price_strat = self.__qty * self.__price

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
