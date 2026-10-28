#!/usr/bin/env python3
"""Revisa que tu equipo esté listo para el taller. Nunca imprime secretos.

    python3 herramientas/doctor.py            # revisión local, sin red
    python3 herramientas/doctor.py --red      # además prueba el token contra la API de INEGI
                                              # (la primera vez descarga ~8 MB de catálogos)
    python3 herramientas/doctor.py --modelo   # además pide una respuesta al modelo con pi (gasta una solicitud)
"""
from __future__ import annotations  # para que el diagnóstico corra incluso en un Python viejo y lo reporte

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

PYTHON_MINIMO = (3, 10)
NODE_MINIMO = (22, 19)
VARIABLES_MODELO = ("GEMINI_API_KEY", "CEREBRAS_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
                    "OPENAI_API_KEY", "ANTHROPIC_API_KEY")


def parsear_version(texto: str) -> tuple | None:
    m = re.search(r"(\d+)\.(\d+)", texto or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def version_de(programa: str) -> tuple | None:
    """(mayor, menor) de `programa --version`, o None si no está instalado o no responde."""
    ruta = shutil.which(programa)
    if not ruta:
        return None
    try:
        salida = subprocess.run([ruta, "--version"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return parsear_version(salida.stdout + salida.stderr)


def _con_offline(funcion):
    """Ejecuta funcion() con INEGI_OFFLINE=1 y deja el entorno como estaba."""
    previo = os.environ.get("INEGI_OFFLINE")
    os.environ["INEGI_OFFLINE"] = "1"
    try:
        return funcion()
    finally:
        if previo is None:
            os.environ.pop("INEGI_OFFLINE", None)
        else:
            os.environ["INEGI_OFFLINE"] = previo


def revisar(red: bool = False, modelo: bool = False) -> list[tuple[str, bool, str]]:
    """Lista de (revisión, pasó, detalle). El detalle nunca contiene secretos."""
    r = []
    py = sys.version_info[:2]
    r.append((f"Python {PYTHON_MINIMO[0]}.{PYTHON_MINIMO[1]} o más reciente", py >= PYTHON_MINIMO,
              f"tienes {py[0]}.{py[1]}" + ("" if py >= PYTHON_MINIMO else ": instala uno nuevo desde python.org")))

    node = version_de("node")
    r.append((f"Node.js {NODE_MINIMO[0]}.{NODE_MINIMO[1]} o más reciente", node is not None and node >= NODE_MINIMO,
              "no encontrado: instálalo desde nodejs.org" if node is None else f"tienes {node[0]}.{node[1]}"))

    pi = version_de("pi")
    r.append(("pi instalado", pi is not None,
              "no encontrado: ver docs/00_PREPARACION.md" if pi is None else f"versión {pi[0]}.{pi[1]}"))

    token = os.environ.get("INEGI_TOKEN", "").strip()
    r.append(("INEGI_TOKEN exportado en esta terminal", bool(token),
              "presente (no se muestra)" if token
              else 'falta: export INEGI_TOKEN="..."  (Windows: $env:INEGI_TOKEN="...")'))

    skills = sorted(p.parent.name for p in (RAIZ / ".agents" / "skills").glob("*/SKILL.md"))
    r.append(("Skills del repo", len(skills) >= 4,
              ", ".join(skills) if skills else "no se encontraron: corre esto desde la carpeta del repo"))

    credencial = (any(os.environ.get(v) for v in VARIABLES_MODELO)
                  or (Path.home() / ".pi" / "agent" / "auth.json").exists())
    r.append(("Credencial de un proveedor de modelo", credencial,
              "encontrada" if credencial else "no encontrada: dentro de pi escribe /login"))

    inegi = None
    try:
        import inegi
        ficha = _con_offline(lambda: inegi.ficha("910392"))
        r.append(("Herramienta inegi.py sin red (fixtures)", "Precios al Consumidor" in ficha["fuente"],
                  f"ficha del INPC leída: {ficha['unidad']}"))
    except Exception as e:  # queremos reportar cualquier fallo sin detener el diagnóstico
        r.append(("Herramienta inegi.py sin red (fixtures)", False, f"error: {e}"))

    if red:
        if not token or inegi is None:
            r.append(("API de INEGI con red", False, "no se puede probar sin token o sin la herramienta"))
        else:
            try:
                resultados = inegi.validar("910392")
                ok = all(paso for paso, _ in resultados)
                r.append(("API de INEGI con red", ok, "la serie 910392 coincide con lo esperado" if ok
                          else "algo no coincide: corre  python3 herramientas/inegi.py validar 910392"))
            except Exception as e:
                r.append(("API de INEGI con red", False, inegi._redactar(str(e))))

    if modelo:
        r.append(probar_modelo())
    return r


def probar_modelo() -> tuple[str, bool, str]:
    """Pide a pi una respuesta de una palabra. Gasta una solicitud del plan del modelo."""
    nombre = "El modelo responde (pi -p)"
    if not shutil.which("pi"):
        return (nombre, False, "pi no está instalado")
    try:
        salida = subprocess.run(["pi", "-p", "-ns", "-nc", "Responde solo con la palabra: listo"],
                                capture_output=True, text=True, timeout=180, cwd=RAIZ)
    except subprocess.TimeoutExpired:
        return (nombre, False, "sin respuesta en 3 minutos: revisa /login y la red")
    texto = (salida.stdout + salida.stderr).strip()
    ok = "listo" in texto.lower()
    return (nombre, ok, "respondió" if ok else f"respuesta inesperada: {texto[:120]}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--red", action="store_true", help="probar el token contra la API de INEGI")
    p.add_argument("--modelo", action="store_true", help="pedir una respuesta al modelo con pi (gasta una solicitud)")
    a = p.parse_args(argv)
    resultados = revisar(red=a.red, modelo=a.modelo)
    for nombre, ok, detalle in resultados:
        print(f"{'[OK]   ' if ok else '[FALTA]'} {nombre}: {detalle}")
    faltan = [n for n, ok, _ in resultados if not ok]
    if faltan:
        print(f"\nFaltan {len(faltan)} cosas. Revisa docs/00_PREPARACION.md o pide ayuda antes del taller.")
        return 1
    print("\nTodo listo." + ("" if a.red else " Con --red también pruebas el token; con --modelo, el modelo."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
