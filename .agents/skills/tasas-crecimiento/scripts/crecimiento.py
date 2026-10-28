#!/usr/bin/env python3
"""Tasas de crecimiento de una serie guardada como CSV (columnas periodo,valor).

    python3 .agents/skills/tasas-crecimiento/scripts/crecimiento.py investigacion/datos/910392.csv --tipo anual
    python3 .agents/skills/tasas-crecimiento/scripts/crecimiento.py investigacion/datos/736181.csv \
        --tipo cagr --desde 2010/04 --hasta 2019/04
"""
from __future__ import annotations

import argparse
import csv
import sys


def leer_csv(ruta: str) -> dict:
    with open(ruta, newline="", encoding="utf-8") as fh:
        return {r["periodo"]: float(r["valor"]) for r in csv.DictReader(fh) if r["valor"] != ""}


def periodo_anterior(periodo: str) -> str:
    """Mismo periodo del año anterior: '2026/09' -> '2025/09', '2026/02' (trimestre) -> '2025/02', '2026' -> '2025'."""
    return str(int(periodo[:4]) - 1) + periodo[4:]


def variacion_anual(valores: dict, periodo: str) -> float | None:
    previo = periodo_anterior(periodo)
    if periodo not in valores or previo not in valores or valores[previo] == 0:
        return None
    return (valores[periodo] / valores[previo] - 1) * 100


def cagr(valores: dict, desde: str, hasta: str) -> float:
    """Tasa de crecimiento anual compuesta entre dos periodos que deben ser el MISMO mes o trimestre."""
    if desde[4:] != hasta[4:]:
        raise ValueError("Usa el mismo mes o trimestre en 'desde' y 'hasta' (p. ej. 2010/04 y 2019/04).")
    for p in (desde, hasta):
        if p not in valores:
            raise ValueError(f"El periodo {p} no está en la serie.")
    anios = int(hasta[:4]) - int(desde[:4])
    if anios <= 0:
        raise ValueError("'hasta' debe ser posterior a 'desde'.")
    return ((valores[hasta] / valores[desde]) ** (1 / anios) - 1) * 100


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--tipo", choices=["anual", "cagr"], default="anual")
    p.add_argument("--desde")
    p.add_argument("--hasta")
    p.add_argument("--ultimos", type=int, default=12, help="cuántos periodos mostrar (tipo anual)")
    a = p.parse_args(argv)
    valores = leer_csv(a.csv)
    try:
        if a.tipo == "cagr":
            if not (a.desde and a.hasta):
                raise ValueError("El tipo cagr necesita --desde y --hasta.")
            print(f"Crecimiento anual compuesto {a.desde} -> {a.hasta}: {cagr(valores, a.desde, a.hasta):.2f}%")
        else:
            print("periodo      valor            variación anual (%)")
            for periodo in sorted(valores)[-a.ultimos:]:
                v = variacion_anual(valores, periodo)
                print(f"{periodo:<10} {valores[periodo]:>14.3f}   {'' if v is None else f'{v:.2f}'}")
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
