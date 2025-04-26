import unittest
import pandas as pd
from taux import Taux

class TestTaux(unittest.TestCase):

    def setUp(self):
        self.taux = Taux()
        # Crée un échéancier bien compris entre les dates du fichier Taux.xlsx
        self.echeancier = pd.date_range(start="2026-01-01", end="2030-01-01", freq='3ME').to_list()

    def test_Courbe_TauxZC_calculation(self):
        self.taux.Courbe_TauxZC(self.echeancier)
        zc = self.taux.get_ZC()

        # Vérifie qu'on a bien un TauxZC pour chaque date
        self.assertEqual(len(zc), len(self.echeancier))
        self.assertFalse(zc['TauxZC'].isnull().any())  # Aucune valeur manquante

    def test_get_set_ZC(self):
        df = pd.DataFrame({"Date": pd.date_range(start="2025-01-01", periods=5), "TauxZC": [0.02]*5})
        self.taux.set_ZC(df)
        self.assertTrue(self.taux.get_ZC().equals(df))

    def test_set_get_Fwd(self):
        df = pd.DataFrame({"Date": pd.date_range(start="2025-01-01", periods=5), "TauxFWD": [0.021]*5})
        self.taux.set_Fwd(df)
        self.assertTrue(self.taux.get_Fwd().equals(df))

    def test_Courbe_TauxFWD_calculation(self):
        self.taux.Courbe_TauxZC(self.echeancier)
        self.taux.Courbe_TauxFWD()
        fwd = self.taux.get_Fwd()

        self.assertEqual(len(fwd), len(self.echeancier))
        self.assertFalse(fwd['TauxFWD'].isnull().any())

if __name__ == '__main__':
    unittest.main()
