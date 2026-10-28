"""Pruebas del script de la skill tasas-crecimiento, contra cifras conocidas (anclas)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
sys.path.insert(0, str(RAIZ / ".agents" / "skills" / "tasas-crecimiento" / "scripts"))
import crecimiento  # noqa: E402
import inegi  # noqa: E402


class TestCrecimiento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with mock.patch.dict(os.environ, {"INEGI_OFFLINE": "1"}):
            cls.dir = tempfile.TemporaryDirectory()
            for i in ("910392", "736181"):
                inegi.escribir_csv(inegi.obtener_serie(i), Path(cls.dir.name) / f"{i}.csv")
        cls.inpc = crecimiento.leer_csv(f"{cls.dir.name}/910392.csv")
        cls.pib = crecimiento.leer_csv(f"{cls.dir.name}/736181.csv")

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def test_periodo_anterior(self):
        self.assertEqual(crecimiento.periodo_anterior("2026/09"), "2025/09")
        self.assertEqual(crecimiento.periodo_anterior("2026/02"), "2025/02")
        self.assertEqual(crecimiento.periodo_anterior("2026"), "2025")

    def test_inflacion_anual_septiembre_2026_es_3_45(self):
        self.assertAlmostEqual(crecimiento.variacion_anual(self.inpc, "2026/09"), 3.45, places=2)

    def test_pico_de_inflacion_septiembre_2022_es_8_7(self):
        self.assertAlmostEqual(crecimiento.variacion_anual(self.inpc, "2022/09"), 8.70, places=2)

    def test_primer_periodo_no_tiene_variacion_anual(self):
        self.assertIsNone(crecimiento.variacion_anual(self.inpc, "1969/01"))

    def test_cagr_del_pib_2010_2019_y_2019_2025(self):
        self.assertAlmostEqual(crecimiento.cagr(self.pib, "2010/04", "2019/04"), 1.80, places=2)
        self.assertAlmostEqual(crecimiento.cagr(self.pib, "2019/04", "2025/04"), 1.18, places=2)

    def test_cagr_exige_el_mismo_trimestre(self):
        with self.assertRaisesRegex(ValueError, "mismo mes o trimestre"):
            crecimiento.cagr(self.pib, "2010/01", "2019/04")

    def test_cagr_rechaza_periodos_invertidos(self):
        with self.assertRaisesRegex(ValueError, "posterior"):
            crecimiento.cagr(self.pib, "2019/04", "2010/04")


if __name__ == "__main__":
    unittest.main()
