---
name: tasas-crecimiento
description: Calcula variaciones anuales y tasas de crecimiento compuesto (CAGR) de series de INEGI guardadas como CSV. Úsala cuando se pida inflación anual, crecimiento anual del PIB, tasa de crecimiento entre dos fechas o cualquier variación porcentual de una serie.
---

# Tasas de crecimiento

Script: `.agents/skills/tasas-crecimiento/scripts/crecimiento.py` (lee los CSV que genera `inegi.py serie`).

## Uso

```
# variación anual de los últimos 12 periodos
python3 .agents/skills/tasas-crecimiento/scripts/crecimiento.py investigacion/datos/910392.csv --tipo anual

# crecimiento anual compuesto entre dos periodos (mismo mes o trimestre)
python3 .agents/skills/tasas-crecimiento/scripts/crecimiento.py investigacion/datos/736181.csv \
    --tipo cagr --desde 2010/04 --hasta 2019/04
```

## Reglas

- **Variación anual** = valor del periodo / valor del **mismo periodo del año anterior** − 1. Para series originales
  es la comparación correcta porque evita la estacionalidad. No compares un mes contra el mes anterior en una serie original.
- **CAGR** = (final / inicial)^(1 / años) − 1. Usa el mismo mes o trimestre en los dos extremos.
- La inflación anual es la variación anual del INPC (`910392`).
- Una variación de una serie en **índice** no es lo mismo que una diferencia en **puntos porcentuales** (tasas como la
  desocupación se restan, no se dividen).
- Si el periodo anterior no existe en la serie, el script deja la variación vacía. No la inventes.

## Cifras de referencia (para comprobar que el script funciona)

| Cálculo | Resultado |
|---|---|
| INPC `910392`, variación anual septiembre 2026 | 3.45 % |
| INPC `910392`, variación anual septiembre 2022 (pico) | 8.70 % |
| PIB `736181`, CAGR 2010/04 → 2019/04 | 1.80 % |
| PIB `736181`, CAGR 2019/04 → 2025/04 | 1.18 % |

INEGI puede revisar series históricas: una diferencia mínima es normal, una grande hay que investigarla.
