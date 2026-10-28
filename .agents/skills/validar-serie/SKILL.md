---
name: validar-serie
description: Verifica que una serie de INEGI es realmente la que se cree antes de usarla en un resultado. Úsala siempre que se vaya a citar, graficar o analizar una serie, o cuando el nombre de una serie parezca ambiguo.
---

# Validar una serie antes de usarla

Un ID equivocado produce una conclusión equivocada con cifras que parecen reales. Valida en cuatro capas.

## Procedimiento

1. **Ficha.** `python3 herramientas/inegi.py ficha <ID>`. Anota hoja, tema, unidad, frecuencia, fuente y última actualización.
   El nombre de la hoja solo no basta: «Total» aparece 2,455 veces en el catálogo, «Índice» 1,139.
2. **¿Coincide con lo que buscamos?** Contrasta contra la pregunta de investigación:
   - ¿Es serie **original** o **desestacionalizada**? (el tema lo dice)
   - ¿La unidad es la correcta? (nivel, índice con base, variación %, pesos corrientes o constantes)
   - ¿La frecuencia coincide con el análisis? (mensual, trimestral)
   - ¿La fuente es el programa esperado? (INPC, IGAE, ENOE, PIB trimestral)
3. **Si está en `datos/series_validadas.json`:** `python3 herramientas/inegi.py validar <ID>`. Comprueba la ficha
   y las **anclas** (cifras publicadas por INEGI que la serie debe reproducir). Si algo falla, no uses la serie.
4. **Si no está en la tabla:** busca una cifra publicada por INEGI (boletín de prensa o Constructor de consultas)
   y compárala con la serie. Si no puedes contrastarla, **dilo** en el resultado como limitación.

## Formato de la ficha en cualquier resultado

```
Serie 910392 — Índice Nacional de Precios al Consumidor, índice general
Unidad: Índice base 2018=100 · Mensual · Serie original
Fuente: INEGI. INPC 2018 · Actualizada: 08/10/2026 · Validada: sí (ficha + 2 anclas)
```

## Errores que esta skill existe para evitar

- Usar `216064`, `628194` o `628229` para el INPC (sin datos o desactualizadas desde 2024).
- Tomar `737173` (solo actividades secundarias) o `737151` (un subsector) por el IGAE total (`737121`).
- Comparar una serie original con una desestacionalizada, o trimestres distintos de una serie original.
- Citar un nombre de hoja como si fuera el nombre de la serie.

## Regla

Si una validación falla, **no continúes con esa serie**. Explica qué no coincide y propón la alternativa.
