import numpy as np
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Maturite:
    """
    Classe Maturite : Représente la maturité d'un produit.
    """

    def __init__(self, T: float, fixing: None) -> None:
        """
        Constructeur de la classe Maturite.
        """
        self.__T = T
        self.__fixing = fixing
        self.__start_date = datetime.strptime(str(date.today()), "%Y-%m-%d")
        self.__DateMaturite = None

    def ExpiryDate(self):

        adjusted = self.__start_date + relativedelta(years=self.__T)
        self.__DateMaturite = np.busday_offset(
            np.datetime64(adjusted.date()), 0, roll="forward"
        )
        return self.__DateMaturite

    def CreationEcheancier(self) -> list:
        echeancier = list()
        date_iter = self.__start_date
        match self.__fixing:
            case "Trimestriel":
                date_iter += relativedelta(months=3)
            case "Semestriel":
                date_iter += relativedelta(months=6)
            case "Annuel":
                date_iter += relativedelta(years=1)

        while date_iter <= datetime.strptime(str(self.__DateMaturite), "%Y-%m-%d"):
            date64 = np.datetime64(date_iter.date())
            inter = np.busday_offset(date64, 0, roll="forward")
            echeancier.append(datetime.strptime(str(inter), "%Y-%m-%d"))

            match self.__fixing:
                case "Trimestriel":
                    date_iter += relativedelta(months=3)
                case "Semestriel":
                    date_iter += relativedelta(months=6)
                case "Annuel":
                    date_iter += relativedelta(years=1)
        return echeancier
