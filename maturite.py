class Maturite:
    """
    Classe Maturite : Représente la maturité d'un produit.
    """

    #    def __init__(self, type_option, strike, maturite):
    #         self.type = type_option
    #         self.strike = strike
    #         self.maturite = maturite

    def __init__(self, T, fixing) -> None:
        """
        Constructeur de la classe Maturite.
        """
        self.T = T
        self.fixing = fixing
