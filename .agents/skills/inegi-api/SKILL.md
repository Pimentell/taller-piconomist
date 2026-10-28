---
name: inegi-api
description: Consulta series económicas de INEGI (INPC, PIB, desocupación, IGAE) con la herramienta herramientas/inegi.py. Úsala cuando haya que buscar, descargar o identificar una serie de INEGI, o cuando falle una consulta a la API.
---

# Consultar la API de INEGI

Todo se hace con `python3 herramientas/inegi.py` desde la raíz del repo (en Windows, `python`).

| Necesito... | Comando |
|---|---|
| Ver qué series ya están validadas | `inegi.py validadas` |
| Identificar una serie | `inegi.py ficha <ID>` |
| Descargar una serie a CSV | `inegi.py serie <ID>` (guarda en `investigacion/datos/<ID>.csv`) |
| Comprobar que una serie es la esperada | `inegi.py validar <ID>` |
| Buscar por texto | `inegi.py buscar "texto"` (poco confiable, ver abajo) |

## Cómo se elige una serie

1. **Empieza por `validadas`.** Es la lista de series ya identificadas y contrastadas.
2. Si necesitas otra, `buscar` solo busca en el **nombre de la hoja** del catálogo. Por eso `buscar "desocupación"`
   devuelve series de la ENOE pero no la `444884` (que en el catálogo se llama solo «Índice»), y
   `buscar "inflación"` no devuelve nada. El descubrimiento fiable se hace en el *Constructor de consultas* de INEGI
   (enlace en https://www.inegi.org.mx/servicios/api_indicadores.html).
3. Cualquier ID nuevo pasa por `ficha` y por la skill `validar-serie` **antes** de usarse.

## Trampas conocidas de la API

- **Fuente `BIE-BISE` y área `00`.** El cliente ya lo hace. Con la fuente `BIE` o `BISE` solas, muchas series responden
  «No se encontraron resultados» (HTTP 400) aunque existan.
- **Orden:** la API entrega de la observación más reciente a la más antigua. El cliente ya ordena de antigua a reciente.
- **Valores como texto:** `OBS_VALUE` llega como cadena. El cliente los convierte a número.
- **IDs que ya no sirven:** `216064` (INPC viejo) no devuelve datos; `628194` y `628229` se quedaron en 2024.
  El INPC vigente es `910392`.
- **El token no se valida de forma visible:** la API puede responder datos con un token incorrecto. Que una consulta
  funcione no prueba que el token sea bueno. INEGI podría exigirlo en cualquier momento.
- **Mismo nombre, series distintas:** en el IGAE, `737121` es el total (serie original), `737173` solo actividades
  secundarias y `737151` un subsector de energía. Nunca confíes en el nombre de la hoja.

## Si falla

- `ERROR: Falta la variable INEGI_TOKEN`: el token no está exportado en esta terminal. Ver `docs/00_PREPARACION.md`.
- `No se encontraron resultados`: revisa el ID. No intentes otras fuentes al azar.
- Sin internet o sin token: `INEGI_OFFLINE=1` usa respuestas guardadas para 4 series (`910392`, `444884`,
  `736181`, `737121`). Avisa a la persona que son datos guardados, no una consulta nueva.

## Cómo agregar una serie validada

Edita `datos/series_validadas.json` solo después de: (1) `ficha`, (2) contrastar con INEGI (boletín o Constructor de
consultas), (3) definir al menos las expectativas de tema, unidad, frecuencia y fuente. Si tiene una cifra
publicada por INEGI, agrégala como ancla.
