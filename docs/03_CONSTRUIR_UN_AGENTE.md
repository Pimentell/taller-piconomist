# 03 · Cómo se construye un agente

Ya usaste un agente (pi). Aquí se ve por dentro, con Python, qué lo compone. Un agente es **un modelo de lenguaje +
herramientas + un bucle**, rodeado de contexto y de límites.

## Las piezas

| Pieza | Qué es | Dónde la ves |
|---|---|---|
| **Modelo** | el LLM; predice texto, no sabe cifras de INEGI | `llamar_modelo()` en `ejemplos/agente_minimo.py`; `/model` en pi |
| **Instrucciones** | el prompt de sistema: rol y reglas | `SISTEMA` en `agente_minimo.py`; `AGENTS.md` en pi |
| **Herramientas** | funciones que el modelo puede pedir ejecutar | `FUNCIONES` y `DESCRIPCION`; en pi: `read`, `bash`, `edit`, `write`... |
| **Bucle** | pedir → ejecutar → devolver resultado → repetir | `agente()` en `agente_minimo.py` |
| **Contexto / memoria** | la conversación acumulada (cabe una cantidad limitada) | la lista `mensajes`; en pi: sesiones y compactación |
| **Skills** | conocimiento que se carga solo cuando hace falta | `.agents/skills/` |
| **Límites** | qué puede y qué no puede hacer | `max_pasos`; en pi: lista de herramientas y aislamiento |

## Tres formas de construir uno

**A. Configurar un agente existente (lo que hicimos con pi).** Sin programar el bucle: `AGENTS.md` (instrucciones),
skills (conocimiento) y el script `inegi.py` (herramienta que el agente ejecuta con `bash`). Es la forma más rápida y
la que más usarás.

**B. Escribir el bucle tú, en Python (`ejemplos/agente_minimo.py`).** ~80 líneas, sin librerías externas. Sirve para
entender qué pasa dentro. Configura un proveedor (tres variables de entorno, ver el encabezado del archivo) y corre:

```
python3 ejemplos/agente_minimo.py "¿De dónde viene la serie 910392 y cuál es su último dato?"
```

Verás en pantalla cada herramienta que el modelo pide (`[paso 1] herramienta ficha_serie(...)`). Ese es el bucle.

**C. Usar las bibliotecas de pi.** pi está hecho de paquetes que se pueden usar desde código (`pi-ai`,
`pi-agent-core` y el SDK de `pi-coding-agent`). Están escritos en TypeScript, así que quedan fuera de este taller;
si te interesa, empieza por https://github.com/earendil-works/pi

## Ejercicios con `agente_minimo.py`

1. **Léelo completo** (80 líneas). Marca dónde está cada pieza de la tabla.
2. **Cambia el prompt de sistema** para que responda como tutor. ¿Cambia el comportamiento?
3. **Agrega una herramienta** `variacion_anual(id, periodo)` que use `inegi.variacion_anual`. Hay que hacer tres cosas:
   escribir la función, agregarla a `FUNCIONES` y agregar su descripción a `DESCRIPCION`. Si la descripción es mala, el
   modelo no sabrá cuándo usarla (igual que con las skills).
4. **Rómpelo a propósito:** pide el último dato de la serie `216064`. ¿Qué hace el bucle con el error?
5. **Ponle un límite:** baja `max_pasos` a 1. ¿Qué pasa y por qué?

## Seguridad: lo que un bucle no resuelve solo

- El agente **ejecuta lo que el modelo pide**. Si le das `bash`, puede borrar archivos o leer variables de entorno.
- Lo que el agente lee (archivos, respuestas de una API) puede contener instrucciones disfrazadas de datos
  («ignora lo anterior...»). Trátalo como no confiable.
- Dale solo las herramientas que necesita y pídele confirmación para acciones que no se pueden deshacer.
