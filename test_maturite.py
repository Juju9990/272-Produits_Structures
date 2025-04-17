import unittest
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import numpy as np

from maturite import Maturite


class TestMaturite(unittest.TestCase):
    def test_expiry_date_returns_next_business_day(self):
        T = 1  # 1 an
        mat = Maturite(T=T, fixing=None)
        expected = np.datetime64("2026-04-20")

        result = mat.ExpiryDate()

        self.assertEqual(result, expected)

    def test_trimestriel_schedule(self):
        mat = Maturite(T=1, fixing="Trimestriel")
        mat.ExpiryDate()

        # Test de l'échéancier trimestriel
        result = mat.CreationEcheancier()

        self.assertEqual(
            result,
            [
                datetime.strptime(str("2025-07-18"), "%Y-%m-%d"),
                datetime.strptime(str("2025-10-20"), "%Y-%m-%d"),
                datetime.strptime(str("2026-01-19"), "%Y-%m-%d"),
                datetime.strptime(str("2026-04-20"), "%Y-%m-%d"),
            ],
        )

    def test_semestriel_schedule(self):
        mat = Maturite(T=1, fixing="Semestriel")
        mat.ExpiryDate()

        # Test de l'échéancier semestriel
        result = mat.CreationEcheancier()

        self.assertEqual(
            result,
            [
                datetime.strptime(str("2025-10-20"), "%Y-%m-%d"),
                datetime.strptime(str("2026-04-20"), "%Y-%m-%d"),
            ],
        )

    def test_annuel_schedule(self):
        mat = Maturite(T=1, fixing="Annuel")
        mat.ExpiryDate()

        # Test de l'échéancier semestriel
        result = mat.CreationEcheancier()

        self.assertEqual(result, [datetime.strptime(str("2026-04-20"), "%Y-%m-%d")])


if __name__ == "__main__":
    unittest.main()
