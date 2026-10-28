"""Pruebas de doctor.py: no requieren red ni modelo; node y pi se simulan."""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doctor  # noqa: E402


class TestVersiones(unittest.TestCase):
    def test_parsear_version(self):
        self.assertEqual(doctor.parsear_version("v22.23.3"), (22, 23))
        self.assertEqual(doctor.parsear_version("0.79.6"), (0, 79))
        self.assertIsNone(doctor.parsear_version("sin número"))
        self.assertIsNone(doctor.parsear_version(""))

    def test_programa_ausente(self):
        with mock.patch("shutil.which", return_value=None):
            self.assertIsNone(doctor.version_de("programa-que-no-existe"))


class TestRevision(unittest.TestCase):
    def test_todo_presente_y_el_token_no_se_muestra(self):
        with mock.patch.dict(os.environ, {"INEGI_TOKEN": "secreto-xyz"}), \
                mock.patch.object(doctor, "version_de", return_value=(99, 0)):
            resultados = doctor.revisar()
        por_nombre = {n: ok for n, ok, _ in resultados}
        self.assertTrue(por_nombre["INEGI_TOKEN exportado en esta terminal"])
        self.assertTrue(por_nombre["Node.js 22.19 o más reciente"])
        self.assertTrue(por_nombre["pi instalado"])
        self.assertTrue(por_nombre["Skills del repo"])
        self.assertTrue(por_nombre["Herramienta inegi.py sin red (fixtures)"])
        self.assertNotIn("secreto-xyz", str(resultados))

    def test_sin_token_ni_node_ni_pi(self):
        with mock.patch.dict(os.environ, {"INEGI_TOKEN": ""}), \
                mock.patch.object(doctor, "version_de", return_value=None):
            por_nombre = {n: ok for n, ok, _ in doctor.revisar()}
        self.assertFalse(por_nombre["INEGI_TOKEN exportado en esta terminal"])
        self.assertFalse(por_nombre["Node.js 22.19 o más reciente"])
        self.assertFalse(por_nombre["pi instalado"])

    def test_red_sin_token_no_intenta_conectar(self):
        with mock.patch.dict(os.environ, {"INEGI_TOKEN": ""}), \
                mock.patch.object(doctor, "version_de", return_value=(99, 0)):
            por_nombre = {n: (ok, d) for n, ok, d in doctor.revisar(red=True)}
        self.assertFalse(por_nombre["API de INEGI con red"][0])
        self.assertIn("sin token", por_nombre["API de INEGI con red"][1])

    def test_el_entorno_offline_se_restaura(self):
        with mock.patch.dict(os.environ, {"INEGI_TOKEN": "x"}), \
                mock.patch.object(doctor, "version_de", return_value=(99, 0)):
            os.environ.pop("INEGI_OFFLINE", None)
            doctor.revisar()
            self.assertNotIn("INEGI_OFFLINE", os.environ)


class TestSalida(unittest.TestCase):
    def test_devuelve_1_si_falta_algo(self):
        with mock.patch.object(doctor, "revisar", return_value=[("algo", False, "falta")]), \
                redirect_stdout(io.StringIO()) as buf:
            self.assertEqual(doctor.main([]), 1)
        self.assertIn("[FALTA]", buf.getvalue())

    def test_devuelve_0_si_todo_pasa(self):
        with mock.patch.object(doctor, "revisar", return_value=[("algo", True, "ok")]), \
                redirect_stdout(io.StringIO()) as buf:
            self.assertEqual(doctor.main([]), 0)
        self.assertIn("Todo listo", buf.getvalue())

    def test_probar_modelo_sin_pi(self):
        with mock.patch("shutil.which", return_value=None):
            _, ok, detalle = doctor.probar_modelo()
        self.assertFalse(ok)
        self.assertIn("pi no está instalado", detalle)


if __name__ == "__main__":
    unittest.main()
