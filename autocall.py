from produit import Produit
from fonctionsannexes import *
import pandas as pd
import numpy as np


class Autocall(Produit):
    def __init__(
        self,
        nominal: float,
        T: float,
        fixing: str,
        sous_jacent: str,
        echeancier_fixing: pd.DataFrame,
        echeancier_simulation: pd.DataFrame,
        coupon: float,
        barriere_autocall: float,
        PDI_Strike: float,
        PDI_barriere: float,
        ZC: pd.DataFrame,
    ):
        super().__init__(nominal, T, fixing)
        self.__sous_jacent = sous_jacent
        match self.get_fixing():
            case "Trimestriel":
                self.__coupon = coupon / 3
            case "Semestriel":
                self.__coupon = coupon / 2
            case "Annuel":
                self.__coupon = coupon
        self.__barriere_autocall = barriere_autocall
        self.__PDI_Strike = PDI_Strike
        self.__PDI_barriere = PDI_barriere
        self.__echeancier_fixing = echeancier_fixing
        self.__echeancier_simulation = echeancier_simulation
        self.__liste_fixing = list()
        for i in range(1, len(self.__echeancier_fixing)):
            self.__liste_fixing.append(self.__echeancier_fixing[i][1])
        self.__ZC = ZC
        self.__spot = 0
        self.__v0 = 0
        self.__theta = 0
        self.__kappa = 0
        self.__sigma = 0
        self.__rho = 0
        self.__Calibration_Heston = list()
        self.__prix = 0
        self.__prix_dollar = 0

    def CoursSpot(self):
        match self.__sous_jacent:
            case "Apple":
                target_date = "2025-04-17"
                ticker = yf.Ticker("AAPL")
                historical_data = ticker.history(start=target_date, end="2025-04-18")
                self.__spot = historical_data.loc[target_date]["Close"]

    def Calibration_Heston(self):
        self.__Calibration_Heston = CalibrationHeston(self.__sous_jacent, self.__ZC)
        self.__v0 = self.__Calibration_Heston["v0"]
        self.__theta = self.__Calibration_Heston["theta"]
        self.__kappa = self.__Calibration_Heston["kappa"]
        self.__sigma = self.__Calibration_Heston["sigma"]
        self.__rho = self.__Calibration_Heston["rho"]

    def MonteCarlo(self):
        """Calcule le prix du produit"""
        payoff = list()
        MCarlo = 100
        np.random.seed(42)
        for i in range(MCarlo):
            compteur_fixing = 1
            V = list()
            S = list()
            V.append(self.__v0)
            S.append(self.__spot)
            X = np.random.randn(self.__echeancier_fixing[-1][1])
            Y = np.random.randn(self.__echeancier_fixing[-1][1])
            for j in range(self.__echeancier_fixing[-1][1]):
                Z1 = X[j]
                Z2 = self.__rho * X[j] + np.sqrt(1 - self.__rho**2) * Y[j]
                delta_t = (
                    pd.Timestamp(self.__echeancier_simulation[j + 1])
                    - pd.Timestamp(self.__echeancier_simulation[j])
                ).days / 365
                S.append(
                    S[j]
                    * np.exp(
                        (
                            self.__ZC[
                                self.__ZC["Date"] == self.__echeancier_simulation[j + 1]
                            ]["TauxZC"].values[0]
                            - 0.5 * V[j]
                        )
                        * delta_t
                        + np.sqrt(V[j] * delta_t) * Z2
                    )
                )
                V.append(
                    max(
                        0,
                        V[j]
                        + self.__kappa * (self.__theta - V[j]) * delta_t
                        + self.__sigma * np.sqrt(V[j] * delta_t) * Z1,
                    )
                )
                if j + 1 in self.__liste_fixing:
                    if j + 1 != self.__echeancier_fixing[-1][1]:
                        if S[j + 1] >= self.__spot * self.__barriere_autocall:
                            t = (
                                pd.Timestamp(self.__echeancier_simulation[j + 1])
                                - pd.Timestamp(self.__echeancier_fixing[0][0])
                            ).days / 365
                            self.__prix = np.exp(
                                -self.__ZC[
                                    self.__ZC["Date"]
                                    == self.__echeancier_simulation[j + 1]
                                ]["TauxZC"].values[0]
                                * t
                            ) * (1 + self.__coupon * compteur_fixing)
                            break
                    else:
                        t = (
                            pd.Timestamp(self.__echeancier_fixing[-1][0])
                            - pd.Timestamp(self.__echeancier_fixing[0][0])
                        ).days / 365
                        if S[j + 1] >= self.__spot * self.__barriere_autocall:
                            self.__prix = np.exp(
                                -self.__ZC[
                                    self.__ZC["Date"] == self.__echeancier_fixing[-1][0]
                                ]["TauxZC"].values[0]
                                * t
                            ) * (1 + self.__coupon * compteur_fixing)
                            break
                        elif S[j + 1] <= self.__spot * self.__PDI_barriere:
                            self.__prix = np.exp(
                                -self.__ZC[
                                    self.__ZC["Date"] == self.__echeancier_fixing[-1][0]
                                ]["TauxZC"].values[0]
                                * t
                            ) * (1 - S[j + 1] / self.__spot)
                            break
                        else:
                            self.__prix = np.exp(
                                -self.__ZC[
                                    self.__ZC["Date"] == self.__echeancier_fixing[-1][0]
                                ]["TauxZC"].values[0]
                                * t
                            )
                    compteur_fixing += 1
            payoff.append(self.__prix)
        self.__prix = np.mean(payoff)
        self.__prix_dollar = self.get_nominal() * self.__prix

    def Payoff(self, spot):
        """Calcule le payoff du produit à maturité"""
        pass

    def Prix(self):
        """Retourne le prix de la stratégie/produit"""
        pass

    def Description(self):
        """Retourne une description du produit"""
        pass

    def get_calibration(self) -> dict:
        return self.__Calibration_Heston

    def get_prix(self) -> float:
        return self.__prix

    def get_prix_dollar(self) -> float:
        return self.__prix_dollar

    def get_sous_jacent(self) -> dict:
        return self.__sous_jacent
