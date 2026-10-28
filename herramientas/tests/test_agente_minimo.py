"""Pruebas del agente mínimo: el bucle con un modelo simulado y la llamada HTTP contra un servidor local."""
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ejemplos"))
import agente_minimo  # noqa: E402


def modelo_simulado(guion):
    """Devuelve un 'modelo' que responde con los mensajes del guion, en orden, y recuerda lo que recibió."""
    vistos = []

    def llamar(mensajes):
        vistos.append([dict(m) for m in mensajes])
        return guion[len(vistos) - 1]
    llamar.vistos = vistos
    return llamar


def pedir(nombre, args, id_="c1"):
    return {"role": "assistant", "content": None,
            "tool_calls": [{"id": id_, "type": "function",
                            "function": {"name": nombre, "arguments": json.dumps(args)}}]}


class TestBucle(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, {"INEGI_OFFLINE": "1"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_el_modelo_pide_una_herramienta_recibe_el_resultado_y_responde(self):
        llamar = modelo_simulado([pedir("ficha_serie", {"id": "910392"}),
                                  {"role": "assistant", "content": "Es el INPC general."}])
        respuesta = agente_minimo.agente("¿qué es 910392?", llamar=llamar, mostrar=lambda *_: None)
        self.assertEqual(respuesta, "Es el INPC general.")
        resultado = llamar.vistos[1][-1]  # lo último que vio el modelo en la 2.ª llamada
        self.assertEqual(resultado["role"], "tool")
        self.assertEqual(resultado["tool_call_id"], "c1")
        self.assertIn("Índice Nacional de Precios al Consumidor", resultado["content"])

    def test_un_error_de_herramienta_vuelve_al_modelo_como_texto(self):
        llamar = modelo_simulado([pedir("ficha_serie", {"id": "999999"}),
                                  {"role": "assistant", "content": "No pude identificarla."}])
        agente_minimo.agente("x", llamar=llamar, mostrar=lambda *_: None)
        self.assertTrue(llamar.vistos[1][-1]["content"].startswith("ERROR:"))

    def test_herramienta_inexistente_no_rompe_el_bucle(self):
        llamar = modelo_simulado([pedir("inventada", {}), {"role": "assistant", "content": "ok"}])
        self.assertEqual(agente_minimo.agente("x", llamar=llamar, mostrar=lambda *_: None), "ok")
        self.assertTrue(llamar.vistos[1][-1]["content"].startswith("ERROR:"))

    def test_se_detiene_en_el_maximo_de_pasos(self):
        llamar = modelo_simulado([pedir("ultimos_datos", {"id": "910392", "n": 2}, f"c{i}") for i in range(3)])
        respuesta = agente_minimo.agente("x", llamar=llamar, max_pasos=3, mostrar=lambda *_: None)
        self.assertIn("máximo de pasos", respuesta)


class _Falso(BaseHTTPRequestHandler):
    recibido = {}

    def do_POST(self):
        _Falso.recibido = {"ruta": self.path, "auth": self.headers["Authorization"],
                           "cuerpo": json.loads(self.rfile.read(int(self.headers["Content-Length"])))}
        salida = json.dumps({"choices": [{"message": {"role": "assistant", "content": "hola"}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(salida)))
        self.end_headers()
        self.wfile.write(salida)

    def log_message(self, *_):
        pass


class TestLlamadaHTTP(unittest.TestCase):
    def test_envia_modelo_mensajes_herramientas_y_clave(self):
        servidor = HTTPServer(("127.0.0.1", 0), _Falso)
        hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
        hilo.start()
        self.addCleanup(servidor.server_close)
        self.addCleanup(servidor.shutdown)
        env = {"LLM_BASE_URL": f"http://127.0.0.1:{servidor.server_port}/v1/", "LLM_API_KEY": "k", "LLM_MODEL": "m"}
        with mock.patch.dict(os.environ, env):
            mensaje = agente_minimo.llamar_modelo([{"role": "user", "content": "hola"}])
        self.assertEqual(mensaje["content"], "hola")
        self.assertEqual(_Falso.recibido["ruta"], "/v1/chat/completions")
        self.assertEqual(_Falso.recibido["auth"], "Bearer k")
        self.assertEqual(_Falso.recibido["cuerpo"]["model"], "m")
        self.assertEqual([t["function"]["name"] for t in _Falso.recibido["cuerpo"]["tools"]],
                         ["ficha_serie", "ultimos_datos"])


if __name__ == "__main__":
    unittest.main()
