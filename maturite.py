import numpy as np
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class Maturite:

    def __init__(self, T: float, fixing: None) -> None:
        """
        Constructeur de la classe Maturite.
        """
        self.__T = T
        self.__fixing = fixing
        self.__start_date = datetime.strptime(str(np.busday_offset(np.datetime64(date.today()), 0, roll='forward')), "%Y-%m-%d")
        self.__DateMaturite = None
        self.__Echeancier_simulation = list()
        self.__Echeancier_fixing = list()


    def ExpiryDate (self):
        adjusted = self.__start_date + relativedelta(years=self.__T)
        self.__DateMaturite = np.busday_offset(np.datetime64(adjusted.date()), 0, roll='forward')
        self.__Echeancier_fixing.append([pd.Timestamp(self.__DateMaturite), self.__T * 12])
    

    def CreationEcheancier_simulation(self):
        echeancier = [pd.to_datetime(str(self.__start_date))]
        date_iter = self.__start_date
        date_iter += relativedelta(months=1)
        while date_iter <= datetime.strptime(str(self.__DateMaturite), "%Y-%m-%d"):
            date64 = np.datetime64(date_iter.date())  
            inter = np.busday_offset(date64, 0, roll='forward')
            echeancier.append(pd.Timestamp(inter))
            date_iter += relativedelta(months=1)
        self.__Echeancier_simulation = echeancier

    def CreationEcheancier_fixing(self):
        if self.__fixing != None:
            compteur = 0
            echeancier = [[pd.to_datetime(str(self.__start_date)), compteur]]
            date_iter = self.__start_date
            match self.__fixing:
                    case "Trimestriel":
                        date_iter += relativedelta(months=3)
                        compteur += 3
                    case "Semestriel":
                        date_iter += relativedelta(months=6)
                        compteur += 6
                    case "Annuel":
                        date_iter += relativedelta(years=1)
                        compteur += 12

            while date_iter <= datetime.strptime(str(self.__DateMaturite), "%Y-%m-%d"):
                date64 = np.datetime64(date_iter.date())
                inter = np.busday_offset(date64, 0, roll='forward')
                echeancier.append([pd.Timestamp(inter), compteur])

                match self.__fixing:
                    case "Trimestriel":
                        date_iter += relativedelta(months=3)
                        compteur += 3
                    case "Semestriel":
                        date_iter += relativedelta(months=6)
                        compteur += 6
                    case "Annuel":
                        date_iter += relativedelta(years=1)
                        compteur += 12
            self.__Echeancier_fixing = echeancier

    def get_T(self) -> float:
        return self.__T
    
    def get_fixing(self) -> str:
        return self.__fixing
    
    def get_startdate(self) -> date:
        return self.__start_date
    
    def get_datematurite(self) -> date:
        return self.__DateMaturite
    
    def get_echeancier_simulation(self) -> list:
        return self.__Echeancier_simulation
    
    def get_echeancier_fixing(self) -> list:
        return self.__Echeancier_fixing
    
    def set_T(self, T) -> None:
        self.__T = T
    
    def set_fixing(self, fixing) -> None:
        self.__fixing = fixing
    
    def set_startdate(self, startdate) -> None:
        self.__start_date = startdate
    
    def set_datematurite(self, datematurite) -> None:
        self.__DateMaturite = datematurite
    
    def set_echeancier_simulation(self, echeancier) -> None:
        self.__Echeancier_simulation = echeancier

    def set_echeancier_fixing(self, echeancier) -> None:
        self.__Echeancier_fixing = echeancier
    