"""Pruebas del cliente de INEGI. Corren sin red, con respuestas reales guardadas en fixtures/.

    python3 -m unittest discover -s herramientas/tests -v
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import inegi  # noqa: E402


class OfflineCase(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, {"INEGI_OFFLINE": "1", "INEGI_TOKEN": "token-secreto-de-prueba"})
        patcher.start()
        self.addCleanup(patcher.stop)


class TestParseo(unittest.TestCase):
    def test_ordena_de_antigua_a_reciente_y_convierte_valores(self):
        texto = json.dumps({"Series": [{"TOPIC": "1", "OBSERVATIONS": [
            {"TIME_PERIOD": "2026/02", "OBS_VALUE": "2.5", "OBS_STATUS": "3"},
            {"TIME_PERIOD": "2026/01", "OBS_VALUE": "", "OBS_STATUS": None}]}]})
        serie = inegi.parsear_serie(texto)
        self.assertEqual([o[0] for o in serie["obs"]], ["2026/01", "2026/02"])
        self.assertIsNone(serie["obs"][0][1])
        self.assertEqual(serie["obs"][1][1], 2.5)
        self.assertNotIn("OBSERVATIONS", serie["meta"])

    def test_cuerpo_de_error_en_lista_levanta_error_claro(self):
        texto = '["ErrorInfo:No se encontraron resultados","ErrorCode:100"]'
        with self.assertRaisesRegex(inegi.ErrorInegi, "No se encontraron resultados.*BIE-BISE"):
            inegi.parsear_serie(texto)

    def test_respuesta_que_no_es_json(self):
        with self.assertRaisesRegex(inegi.ErrorInegi, "no es JSON"):
            inegi.parsear_serie("<html>Página no encontrada</html>")


class TestToken(unittest.TestCase):
    def test_sin_token_da_instrucciones(self):
        with mock.patch.dict(os.environ, {"INEGI_TOKEN": ""}):
            with self.assertRaisesRegex(inegi.ErrorInegi, "INEGI_TOKEN"):
                inegi.token()

    def test_el_token_se_redacta_en_mensajes(self):
        with mock.patch.dict(os.environ, {"INEGI_TOKEN": "abc-123"}):
            self.assertEqual(inegi._redactar("fallo en /abc-123?type=json"), "fallo en /***?type=json")

    def test_url_usa_fuente_y_area_que_funcionan(self):
        url = inegi.url_serie("910392", recientes=False, tok="TOK")
        self.assertIn("/INDICATOR/910392/es/00/false/BIE-BISE/2.0/TOK?type=json", url)


class TestSeries(OfflineCase):
    def test_serie_offline_inpc(self):
        serie = inegi.obtener_serie("910392")
        self.assertEqual(serie["obs"][-1][0], "2026/09")
        self.assertAlmostEqual(serie["obs"][-1][1], 146.075, places=3)

    def test_recientes_devuelve_solo_el_ultimo(self):
        self.assertEqual(len(inegi.obtener_serie("910392", recientes=True)["obs"]), 1)

    def test_serie_sin_fixture_lista_las_disponibles(self):
        with self.assertRaisesRegex(inegi.ErrorInegi, "444884"):
            inegi.obtener_serie("999999")

    def test_ficha_identifica_el_inpc(self):
        f = inegi.ficha("910392")
        self.assertEqual(f["nombre_hoja"], "Índice general")
        self.assertEqual(f["frecuencia"], "Mensual")
        self.assertIn("base 2018", f["unidad"])
        self.assertIn("Índice Nacional de Precios al Consumidor", f["fuente"])

    def test_ficha_distingue_series_de_nombre_ambiguo(self):
        # "Total" (IGAE) y "Valores absolutos" (PIB) solo se entienden con tema, unidad y fuente.
        self.assertIn("volumen físico", inegi.ficha("737121")["tema"])
        self.assertIn("desestacionalizada", inegi.ficha("736181")["tema"])

    def test_buscar_ignora_acentos_y_mayusculas(self):
        ids = [i for i, _ in inegi.buscar("INDICE GENERAL")]
        self.assertIn("910392", ids)


class TestValidacion(OfflineCase):
    def test_validar_inpc_pasa_con_las_anclas_publicadas(self):
        resultados = inegi.validar("910392")
        self.assertTrue(all(ok for ok, _ in resultados), resultados)
        self.assertGreaterEqual(len(resultados), 6)  # 4 campos de la ficha + 2 anclas

    def test_validar_detecta_una_serie_equivocada(self):
        esperado = {"910392": {"unidad_contiene": "pesos a precios de 2018",
                               "anclas": [{"tipo": "nivel", "periodo": "2026/07", "valor": 1.0,
                                           "tolerancia": 0.1, "fuente": "prueba"}]}}
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "v.json"
            ruta.write_text(json.dumps(esperado), encoding="utf-8")
            resultados = inegi.validar("910392", ruta)
        self.assertEqual([ok for ok, _ in resultados], [False, False])

    def test_validar_serie_desconocida(self):
        with self.assertRaisesRegex(inegi.ErrorInegi, "no está en"):
            inegi.validar("736182")

    def test_variacion_anual_inpc_septiembre(self):
        obs = inegi.obtener_serie("910392")["obs"]
        self.assertAlmostEqual(inegi.variacion_anual(obs, "2026/09"), 3.45, places=2)


class TestCLI(OfflineCase):
    def test_serie_escribe_csv_ordenado(self):
        with tempfile.TemporaryDirectory() as d:
            salida = Path(d) / "x.csv"
            with redirect_stdout(io.StringIO()) as buf:
                inegi.main(["serie", "444884", "--salida", str(salida)])
            lineas = salida.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lineas[0], "periodo,valor,estatus")
            self.assertTrue(lineas[1].startswith("2005/01,"))
            self.assertTrue(lineas[-1].startswith("2026/09,"))
            self.assertIn("Serie 444884", buf.getvalue())
            self.assertNotIn("token-secreto-de-prueba", buf.getvalue())

    def test_validadas_lista_las_series_de_la_tabla(self):
        with redirect_stdout(io.StringIO()) as buf:
            inegi.main(["validadas"])
        for id_serie in ("910392", "444884", "736181", "737121"):
            self.assertIn(id_serie, buf.getvalue())

    def test_error_esperado_sale_con_codigo_2(self):
        with self.assertRaises(SystemExit) as cm:
            with mock.patch("sys.stderr", io.StringIO()):
                inegi.main(["ficha", "999999"])
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
