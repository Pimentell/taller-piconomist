#!/usr/bin/env python3
"""Un agente completo en ~80 líneas: modelo + herramientas + bucle. Es lo que pi hace por dentro.

Funciona con cualquier proveedor que acepte el formato "chat completions" con herramientas
(Gemini, Groq, Cerebras, OpenRouter, Ollama...). Configura tres variables de entorno:

    export LLM_BASE_URL="..."   # la URL base de la API de tu proveedor (ver su documentación)
    export LLM_API_KEY="..."
    export LLM_MODEL="..."      # el nombre del modelo en ese proveedor

    python3 ejemplos/agente_minimo.py "¿Cuál es el último dato del INPC y de dónde viene la serie 910392?"

Con INEGI_OFFLINE=1 las herramientas usan las respuestas guardadas en fixtures/.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "herramientas"))
import inegi  # noqa: E402

SISTEMA = ("Eres un asistente de investigación económica. Responde en español. Toda cifra debe venir de una "
           "herramienta; si no puedes obtenerla, dilo. Cita siempre el ID de la serie, la unidad y la fuente.")


# 1) HERRAMIENTAS: funciones normales de Python + una descripción que el modelo puede leer.
def ficha_serie(id: str) -> str:
    return json.dumps(inegi.ficha(id), ensure_ascii=False)


def ultimos_datos(id: str, n: int = 6) -> str:
    return json.dumps(inegi.obtener_serie(id)["obs"][-int(n):], ensure_ascii=False)


FUNCIONES = {"ficha_serie": ficha_serie, "ultimos_datos": ultimos_datos}
DESCRIPCION = [
    {"type": "function", "function": {
        "name": "ficha_serie", "description": "Identifica una serie de INEGI: tema, unidad, frecuencia, fuente.",
        "parameters": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}}},
    {"type": "function", "function": {
        "name": "ultimos_datos", "description": "Últimas n observaciones de una serie de INEGI.",
        "parameters": {"type": "object", "properties": {"id": {"type": "string"}, "n": {"type": "integer"}},
                       "required": ["id"]}}},
]


# 2) MODELO: una llamada HTTP. Recibe la conversación y devuelve el siguiente mensaje.
def llamar_modelo(mensajes: list) -> dict:
    cuerpo = {"model": os.environ["LLM_MODEL"], "messages": mensajes, "tools": DESCRIPCION}
    req = urllib.request.Request(
        os.environ["LLM_BASE_URL"].rstrip("/") + "/chat/completions",
        data=json.dumps(cuerpo).encode(), method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["LLM_API_KEY"]})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["choices"][0]["message"]


# 3) BUCLE: el modelo pide herramientas, nosotros las ejecutamos, le devolvemos el resultado, repetimos.
def ejecutar(llamada: dict) -> str:
    nombre = llamada["function"]["name"]
    try:
        return FUNCIONES[nombre](**json.loads(llamada["function"]["arguments"] or "{}"))
    except Exception as e:  # el error también es información: el modelo lo lee y puede corregir
        return f"ERROR: {e}"


def agente(pregunta: str, llamar=llamar_modelo, max_pasos: int = 8, mostrar=print) -> str:
    mensajes = [{"role": "system", "content": SISTEMA}, {"role": "user", "content": pregunta}]
    for paso in range(1, max_pasos + 1):
        respuesta = llamar(mensajes)
        mensajes.append(respuesta)
        if not respuesta.get("tool_calls"):  # sin herramientas pedidas: es la respuesta final
            return respuesta.get("content") or ""
        for llamada in respuesta["tool_calls"]:
            resultado = ejecutar(llamada)
            mostrar(f"[paso {paso}] herramienta {llamada['function']['name']}({llamada['function']['arguments']})"
                    f" -> {resultado[:120]}")
            mensajes.append({"role": "tool", "tool_call_id": llamada["id"], "content": resultado})
    return "(Se alcanzó el máximo de pasos sin respuesta final.)"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(agente(" ".join(sys.argv[1:])))
