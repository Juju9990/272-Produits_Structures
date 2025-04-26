import unittest
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import numpy as np

from maturite import Maturite

class TestMaturite(unittest.TestCase):
    def test_expiry_date_returns_next_business_day(self):
        T = 1  # 1 an
        mat = Maturite(T=T, fixing=None)
        expected = np.datetime64('2026-04-21')

        result = mat.ExpiryDate()

        self.assertEqual(result, expected)


    def test_trimestriel_schedule(self):
        mat = Maturite(T=1, fixing="Trimestriel")
        mat.ExpiryDate()

        # Test de l'échéancier trimestriel
        result = mat.CreationEcheancier()

        self.assertEqual(result, [datetime.strptime(str('2025-04-21'), "%Y-%m-%d"), datetime.strptime(str('2025-07-21'), "%Y-%m-%d"), datetime.strptime(str('2025-10-21'), "%Y-%m-%d"), datetime.strptime(str('2026-01-21'), "%Y-%m-%d"), datetime.strptime(str('2026-04-21'), "%Y-%m-%d")])


    def test_semestriel_schedule(self):
        mat = Maturite(T=1, fixing="Semestriel")
        mat.ExpiryDate()

        # Test de l'échéancier semestriel
        result = mat.CreationEcheancier()

        self.assertEqual(result, [datetime.strptime(str('2025-04-21'), "%Y-%m-%d"), datetime.strptime(str('2025-10-21'), "%Y-%m-%d"), datetime.strptime(str('2026-04-21'), "%Y-%m-%d")])


    def test_annuel_schedule(self):
        mat = Maturite(T=1, fixing="Annuel")
        mat.ExpiryDate()

        # Test de l'échéancier semestriel
        result = mat.CreationEcheancier()

        self.assertEqual(result, [datetime.strptime(str('2025-04-21'), "%Y-%m-%d"), datetime.strptime(str('2026-04-21'), "%Y-%m-%d")])

    def setUp(self):
        self.mat = Maturite(T=2, fixing="Trimestriel")

    def test_getters_initial_values(self):
        self.assertEqual(self.mat.get_T(), 2)
        self.assertEqual(self.mat.get_fixing(), "Trimestriel")
        self.assertIsInstance(self.mat.get_startdate(), datetime)
        self.assertIsNone(self.mat.get_datematurite())
        self.assertEqual(self.mat.get_echeancier(), [])

    def test_setters(self):
        self.mat.set_T(5)
        self.mat.set_fixing("Annuel")

        new_start = datetime(2022, 1, 1)
        new_maturity = datetime(2027, 1, 1)
        new_echeancier = [datetime(2023, 1, 1), datetime(2024, 1, 1)]

        self.mat.set_startdate(new_start)
        self.mat.set_datematurite(new_maturity)
        self.mat.set_echeancier(new_echeancier)

        self.assertEqual(self.mat.get_T(), 5)
        self.assertEqual(self.mat.get_fixing(), "Annuel")
        self.assertEqual(self.mat.get_startdate(), new_start)
        self.assertEqual(self.mat.get_datematurite(), new_maturity)
        self.assertEqual(self.mat.get_echeancier(), new_echeancier)

if __name__ == '__main__':
    unittest.main()
