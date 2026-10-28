---
name: investigacion-economica
description: Guía el flujo de una investigación económica con datos de INEGI, de la pregunta al informe reproducible. Úsala cuando la persona plantee una pregunta de investigación, pida un análisis con series económicas o quiera redactar resultados.
---

# Flujo de una investigación económica

Sigue los pasos en orden. Cada paso deja evidencia en `investigacion/`.

1. **Pregunta y expectativa.** Reformula la pregunta de forma precisa (variable, periodo, ámbito). Pide a la persona
   su hipótesis o expectativa **antes** de ver los datos, y anótala en `investigacion/informe.md`.
2. **Series.** Elige solo series validadas (`validadas`) o identifica y valida otras con la skill `validar-serie`.
   Anota la ficha de cada una.
3. **Datos.** `inegi.py serie <ID>` por cada serie. Revisa el rango, huecos y valores vacíos antes de calcular.
4. **Transformación.** Antes de comparar o regresar:
   - Series con tendencia (precios, PIB en niveles): trabaja con **variaciones** (anual o contra el mismo periodo
     del año anterior), no con niveles. Ver skill `tasas-crecimiento`.
   - Pesos corrientes → constantes con un deflactor (INPC), no al revés.
   - Frecuencias distintas: agrega a la menor (mensual a trimestral con promedio).
5. **Análisis.** Código en Python en `investigacion/`, que se pueda volver a correr. Prefiere biblioteca estándar;
   si hay pandas o matplotlib instalados puedes usarlos.
6. **Verificación.** Contrasta al menos una cifra con una publicada por INEGI y revisa que el signo y la magnitud
   tengan sentido económico. Si algo sorprende, busca primero un error de datos antes de una explicación económica.
7. **Informe.** `investigacion/informe.md`:

```
# Título (la pregunta)
## Pregunta e hipótesis inicial
## Datos  (una ficha por serie, formato de validar-serie)
## Método (transformaciones, periodo, fórmulas)
## Resultados (cifras con su fuente; tablas y figuras en investigacion/figuras/)
## Interpretación (qué sí y qué no se puede concluir)
## Limitaciones y supuestos
## Cómo reproducir (comandos exactos)
```

## Reglas de interpretación

- Asociación no es causalidad. Escribe «se asocia con», no «causa».
- Una correlación entre dos series con tendencia puede ser un artefacto. Ejemplo real: entre 2022 y 2026 inflación y
  desocupación bajaron juntas y dan una correlación positiva alta (0.77) que **no** es una curva de Phillips.
- Un periodo atípico (COVID 2020–21) cambia los resultados: repite el análisis con y sin él y repórtalo.
- Reporta incertidumbre (error estándar, n) y el tamaño de la muestra.
