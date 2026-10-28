# EJ3 · Escribe tu primera skill: deflactar con el INPC (sesión 2, 45 min)

**Objetivo:** enseñarle al agente un método que ya conoces. Lee antes `docs/02_CREAR_SKILLS.md`.

## Especificación

Crea `.agents/skills/deflactar-inpc/` con:

- `SKILL.md` — cuándo usarla, comando exacto, reglas, cifra de referencia.
- `scripts/deflactar.py` — script en Python que convierte un monto entre dos fechas usando el INPC.

El script debe:
- leer el CSV de la serie `910392` (columnas `periodo,valor`, periodos tipo `2018/12`);
- recibir `--monto`, `--de` y `--a` (usa `argparse`);
- imprimir cuántos pesos de la fecha `--a` equivalen al monto en pesos de la fecha `--de`;
- fallar con un mensaje claro si un periodo no existe.

**Fórmula:** `monto × INPC(a) / INPC(de)`.

## Cifra de referencia (tu prueba)

100 pesos de diciembre de 2018, expresados en pesos de septiembre de 2026, ≈ **141.8** (±0.1).
Si INEGI revisa el INPC, una diferencia mínima es normal; una grande no.

## Pasos

1. Descarga el INPC: pide al agente `descarga la serie 910392` o corre `python3 herramientas/inegi.py serie 910392`.
2. Escribe el script y pruébalo **tú** primero, sin agente.
3. Escribe `SKILL.md` (copia `plantilla-skill/SKILL.md`). Cuida la `description`.
4. En pi: `/reload` y pregunta, sin mencionar la skill: `¿A cuánto equivalen hoy 5,000 pesos de enero de 2020?`
5. ¿La eligió sola? ¿Usó tu script? ¿Pasó por `validar-serie`? Si no, mejora la descripción.

## Preguntas para pensar

- Si deflactas al revés (de 2026 a 2018), ¿qué debe pasar? Pruébalo: debe ser reversible.
- ¿Qué pasa con un salario en pesos corrientes de 2015? ¿Qué base de comparación usarías?
- ¿Por qué el INPC y no otro deflactor? ¿Cuándo no sería adecuado?
