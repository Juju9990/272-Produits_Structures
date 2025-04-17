from produit import Produit
from maturite import Maturite


class Call(Produit):
    def __init__(self, N, T, fixing, K, sous_jacent):
        super().__init__(N, T, fixing)
        self.sous_jacent = sous_jacent
        self.K = K

    def MonteCarlo(self):
        pass

    def Payoff(self, S):
        return max(S - self.K, 0)
