#!/usr/bin/env python3
"""Cliente mínimo de la API de Indicadores de INEGI (solo biblioteca estándar).

Uso desde la terminal (el agente lo ejecuta con la herramienta bash):

    python3 herramientas/inegi.py buscar "precios al consumidor"
    python3 herramientas/inegi.py ficha 910392
    python3 herramientas/inegi.py serie 910392
    python3 herramientas/inegi.py validar 910392
    python3 herramientas/inegi.py validadas

El token se lee de la variable de entorno INEGI_TOKEN y nunca se imprime.
Con INEGI_OFFLINE=1 se usan las respuestas guardadas en fixtures/ (4 series).
"""
from __future__ import annotations  # permite importar el archivo en Python viejo y dar un error claro

import argparse
import csv
import json
import os
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"
FUENTE = "BIE-BISE"  # con "BIE" o "BISE" solos muchas series responden "sin resultados"
AREA = "00"  # nacional
CATALOGOS = ("CL_INDICATOR", "CL_TOPIC", "CL_UNIT", "CL_SOURCE", "CL_FREQ")


class ErrorInegi(Exception):
    """Error esperado: se muestra el mensaje, sin traza."""


def offline() -> bool:
    return os.environ.get("INEGI_OFFLINE") == "1"


def token() -> str:
    valor = os.environ.get("INEGI_TOKEN", "").strip()
    if not valor:
        raise ErrorInegi("Falta la variable INEGI_TOKEN. Pide tu token en "
                         "https://www.inegi.org.mx/app/desarrolladores/generaToken/Usuarios/token_Verify "
                         "y expórtalo en tu terminal (ver docs/00_PREPARACION.md).")
    return valor


def _redactar(texto: str) -> str:
    valor = os.environ.get("INEGI_TOKEN", "")
    return texto.replace(valor, "***") if valor else texto


def _descargar(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8", errors="replace")  # INEGI responde 400 con un cuerpo útil
    except (urllib.error.URLError, TimeoutError) as e:
        raise ErrorInegi(_redactar(f"No se pudo conectar con INEGI: {e}")) from None


def url_serie(id_serie: str, recientes: bool, tok: str, area: str = AREA, fuente: str = FUENTE) -> str:
    r = "true" if recientes else "false"
    return f"{BASE}/INDICATOR/{id_serie}/es/{area}/{r}/{fuente}/2.0/{tok}?type=json"


def parsear_serie(texto: str) -> dict:
    """Devuelve {'meta': {...}, 'obs': [(periodo, valor|None, estatus)]} ordenado de más antiguo a más reciente.

    La API devuelve las observaciones de la más reciente a la más antigua y los valores como texto.
    """
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        raise ErrorInegi("INEGI respondió algo que no es JSON (¿token o servicio caído?).") from None
    if isinstance(datos, list):  # p. ej. ["ErrorInfo:No se encontraron resultados", ...]
        raise ErrorInegi("INEGI respondió: " + "; ".join(str(x) for x in datos)
                         + ". Revisa el ID, el área (00) y la fuente (BIE-BISE).")
    serie = datos["Series"][0]
    obs = []
    for o in serie["OBSERVATIONS"]:
        valor = o["OBS_VALUE"]
        obs.append((o["TIME_PERIOD"], float(valor) if valor not in (None, "") else None, o.get("OBS_STATUS")))
    obs.sort(key=lambda x: x[0])
    meta = {k: v for k, v in serie.items() if k != "OBSERVATIONS"}
    return {"meta": meta, "obs": obs}


def obtener_serie(id_serie: str, recientes: bool = False) -> dict:
    if offline():
        ruta = RAIZ / "fixtures" / "series" / f"{id_serie}.json"
        if not ruta.exists():
            raise ErrorInegi(f"Modo offline: no hay respuesta guardada para {id_serie}. "
                             "Series disponibles: " + ", ".join(sorted(p.stem for p in ruta.parent.glob("*.json"))))
        serie = parsear_serie(ruta.read_text(encoding="utf-8"))
        if recientes:
            serie["obs"] = serie["obs"][-1:]
        return serie
    return parsear_serie(_descargar(url_serie(id_serie, recientes, token())))


# --- catálogos -------------------------------------------------------------------------------------------------

def _dir_cache() -> Path:
    return Path(os.environ.get("INEGI_CACHE", RAIZ / ".cache"))


def cargar_catalogo(nombre: str) -> dict:
    """{código: descripción}. Se descarga una vez (CL_INDICATOR pesa ~7 MB) y se guarda en .cache/."""
    if offline():
        return json.loads((RAIZ / "fixtures" / "catalogos_min.json").read_text(encoding="utf-8"))[nombre]
    ruta = _dir_cache() / f"{nombre}.json"
    if not ruta.exists():
        url = f"{BASE}/{nombre}/null/es/{FUENTE}/2.0/{token()}?type=json"
        texto = _descargar(url)
        try:
            codigos = json.loads(texto)["CODE"]
        except (json.JSONDecodeError, KeyError, TypeError):
            raise ErrorInegi(f"No se pudo descargar el catálogo {nombre}.") from None
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps({c["value"]: c["Description"].strip() for c in codigos}, ensure_ascii=False),
                        encoding="utf-8")
    return json.loads(ruta.read_text(encoding="utf-8"))


def ficha(id_serie: str, serie: dict | None = None) -> dict:
    """Ficha de identidad: nombre de la hoja + tema + unidad + frecuencia + fuente + última actualización."""
    serie = serie or obtener_serie(id_serie, recientes=True)
    m = serie["meta"]
    fuentes = [cargar_catalogo("CL_SOURCE").get(x.strip(), f"(fuente {x.strip()})") for x in m["SOURCE"].split(",")]
    return {
        "id": id_serie,
        "nombre_hoja": cargar_catalogo("CL_INDICATOR").get(id_serie, "(sin nombre en el catálogo)"),
        "tema": cargar_catalogo("CL_TOPIC").get(m["TOPIC"], f"(tema {m['TOPIC']})"),
        "unidad": cargar_catalogo("CL_UNIT").get(m["UNIT"], f"(unidad {m['UNIT']})"),
        "frecuencia": cargar_catalogo("CL_FREQ").get(m["FREQ"], f"(frecuencia {m['FREQ']})"),
        "fuente": " | ".join(fuentes),
        "ultima_actualizacion": m["LASTUPDATE"].split()[0],
        "ultimo_periodo": serie["obs"][-1][0] if serie["obs"] else None,
        "ultimo_valor": serie["obs"][-1][1] if serie["obs"] else None,
    }


def _imprimir_ficha(f: dict) -> None:
    print(f"Serie {f['id']}")
    print(f"  Nombre (hoja): {f['nombre_hoja']}   <- ambiguo por sí solo: se identifica con el resto de la ficha")
    print(f"  Tema:          {f['tema']}")
    print(f"  Unidad:        {f['unidad']}")
    print(f"  Frecuencia:    {f['frecuencia']}")
    print(f"  Fuente:        {f['fuente']}")
    print(f"  Actualizada:   {f['ultima_actualizacion']}")
    print(f"  Último dato:   {f['ultimo_periodo']} = {f['ultimo_valor']}")


def _normalizar(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def buscar(texto: str, limite: int = 20) -> list[tuple[str, str]]:
    palabras = _normalizar(texto).split()
    hallados = [(i, d) for i, d in cargar_catalogo("CL_INDICATOR").items()
                if all(p in _normalizar(d) for p in palabras)]
    return hallados[:limite]


# --- validación ------------------------------------------------------------------------------------------------

def variacion_anual(obs: list, periodo: str) -> float | None:
    valores = {p: v for p, v, _ in obs}
    anterior = str(int(periodo[:4]) - 1) + periodo[4:]
    if valores.get(periodo) is None or valores.get(anterior) in (None, 0):
        return None
    return (valores[periodo] / valores[anterior] - 1) * 100


def validar(id_serie: str, ruta_json: Path | None = None) -> list[tuple[bool, str]]:
    """Compara la ficha (y los datos ancla publicados por INEGI) con lo esperado en datos/series_validadas.json."""
    ruta = ruta_json or RAIZ / "datos" / "series_validadas.json"
    esperado = json.loads(ruta.read_text(encoding="utf-8")).get(id_serie)
    if esperado is None:
        raise ErrorInegi(f"La serie {id_serie} no está en {ruta.name}. Agrégala solo después de identificarla "
                         "con 'ficha' y de contrastarla con INEGI.")
    serie = obtener_serie(id_serie)
    f = ficha(id_serie, serie)
    resultados = []
    for campo in ("tema", "unidad", "frecuencia", "fuente"):
        clave = f"{campo}_contiene"
        if clave in esperado:
            ok = _normalizar(esperado[clave]) in _normalizar(f[campo])
            resultados.append((ok, f"{campo}: esperaba «{esperado[clave]}», ficha dice «{f[campo]}»"))
    valores = {p: v for p, v, _ in serie["obs"]}
    for a in esperado.get("anclas", []):
        if a["tipo"] == "nivel":
            real = valores.get(a["periodo"])
        else:
            real = variacion_anual(serie["obs"], a["periodo"])
        ok = real is not None and abs(real - a["valor"]) <= a["tolerancia"]
        resultados.append((ok, f"ancla {a['tipo']} {a['periodo']}: esperaba {a['valor']} ±{a['tolerancia']}, "
                               f"la serie da {None if real is None else round(real, 3)}  [{a['fuente']}]"))
    if not resultados:
        raise ErrorInegi(f"{id_serie} no tiene verificaciones definidas en datos/series_validadas.json.")
    return resultados


# --- línea de comandos -----------------------------------------------------------------------------------------

def escribir_csv(serie: dict, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["periodo", "valor", "estatus"])
        for p, v, e in serie["obs"]:
            w.writerow([p, "" if v is None else v, e or ""])


def _cmd_serie(a) -> None:
    serie = obtener_serie(a.id, recientes=a.reciente)
    _imprimir_ficha(ficha(a.id, serie))
    ruta = Path(a.salida) if a.salida else Path("investigacion/datos") / f"{a.id}.csv"
    escribir_csv(serie, ruta)
    obs = serie["obs"]
    print(f"\n{len(obs)} observaciones, de {obs[0][0]} a {obs[-1][0]} (ordenadas de antigua a reciente)")
    for p, v, _ in obs[:2] + [("...", None, None)] + obs[-3:] if len(obs) > 5 else obs:
        print(f"  {p:>10}  {'' if v is None else v}")
    print(f"\nGuardado en {ruta}")


def _cmd_ficha(a) -> None:
    _imprimir_ficha(ficha(a.id))


def _cmd_buscar(a) -> None:
    hallados = buscar(a.texto, a.limite)
    if not hallados:
        print("Sin coincidencias.")
    for i, d in hallados:
        print(f"{i:>12}  {d}")
    print("\nOJO: el catálogo solo da el nombre de la hoja (p. ej. «Total»). Antes de usar un ID corre: "
          "inegi.py ficha <ID>")


def _cmd_validar(a) -> None:
    resultados = validar(a.id)
    for ok, texto in resultados:
        print(("[OK]   " if ok else "[FALLA] ") + texto)
    if not all(ok for ok, _ in resultados):
        sys.exit(1)
    print(f"\nLa serie {a.id} coincide con lo esperado.")


def _cmd_validadas(_a) -> None:
    tabla = json.loads((RAIZ / "datos" / "series_validadas.json").read_text(encoding="utf-8"))
    for i, v in tabla.items():
        print(f"{i:>12}  {v['nombre']}")
    print("\nSon las series ya identificadas y contrastadas. Para usar otra: ficha -> contrastar con INEGI -> "
          "agregarla a datos/series_validadas.json.")


def _cmd_catalogos(_a) -> None:
    for nombre in CATALOGOS:
        print(f"{nombre}: {len(cargar_catalogo(nombre))} códigos")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="Cliente de la API de Indicadores de INEGI")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serie", help="descarga una serie y la guarda como CSV")
    s.add_argument("id")
    s.add_argument("--salida", help="ruta del CSV (por defecto investigacion/datos/<id>.csv)")
    s.add_argument("--reciente", action="store_true", help="solo el dato más reciente")
    s.set_defaults(f=_cmd_serie)
    s = sub.add_parser("ficha", help="identifica una serie: hoja, tema, unidad, frecuencia, fuente")
    s.add_argument("id")
    s.set_defaults(f=_cmd_ficha)
    s = sub.add_parser("buscar", help="busca por texto en los nombres del catálogo")
    s.add_argument("texto")
    s.add_argument("--limite", type=int, default=20)
    s.set_defaults(f=_cmd_buscar)
    s = sub.add_parser("validar", help="compara una serie con datos/series_validadas.json")
    s.add_argument("id")
    s.set_defaults(f=_cmd_validar)
    s = sub.add_parser("validadas", help="lista las series ya identificadas y validadas")
    s.set_defaults(f=_cmd_validadas)
    s = sub.add_parser("catalogos", help="descarga y guarda los catálogos (una vez, ~8 MB)")
    s.set_defaults(f=_cmd_catalogos)
    a = p.parse_args(argv)
    try:
        a.f(a)
    except ErrorInegi as e:
        print(f"ERROR: {_redactar(str(e))}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
