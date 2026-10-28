# 01 · Usar el agente

## Arrancar

```
cd taller-agentes-economia                       # la carpeta del material (paso 6 de la preparación)
export INEGI_TOKEN="..."                         # si abriste una terminal nueva
pi -a -ns        # sesión 1: el agente base (instrucciones + herramienta), sin skills
pi -a            # sesión 2: con skills y comandos propios
```

Al abrir pi en esta carpeta:
- Lee `AGENTS.md` automáticamente: es la personalidad y las reglas del agente.
- Descubre las skills de `.agents/skills/`, **pero solo si confías en la carpeta**. Si pi pregunta, responde que sí
  (es tu propio repo). También puedes arrancar con `pi -a` (confiar en los archivos del proyecto en esa ejecución).
  Sin esa confianza las skills del repo **no se cargan** y el agente se comportará como uno sin entrenamiento.
  Si no aparecen: `/trust` y luego `/reload`.

Comandos útiles dentro de pi:

| Comando | Qué hace |
|---|---|
| `/login`, `/model` | conectar proveedor, elegir modelo |
| `/skill:validar-serie 910392` | fuerza el uso de una skill |
| `/reload` | recarga skills y contexto después de editarlos |
| `pi --continue` (en la terminal) | retoma la última sesión de esta carpeta |
| `pi -a` (en la terminal) | arranca confiando en los archivos del proyecto (carga las skills del repo) |
| `pi -ns` (en la terminal) | arranca **sin** skills (para compararlo con y sin) |

## Cosas que pi hace sin preguntarte

**pi ejecuta comandos, lee y edita archivos sin pedir permiso.** Revisa lo que hizo. Por eso el repo trabaja en
`investigacion/`, y por eso el token no debe aparecer en ningún archivo. El agente tiene reglas para no imprimirlo, pero
una regla en un texto no es una barrera: tú eres parte de la seguridad.

## Chatbot o agente: la diferencia son tres banderas

```
pi -nc -ns -nt      # sin contexto (AGENTS.md), sin skills, sin herramientas: un chatbot
pi -a -ns           # con AGENTS.md y herramientas, sin skills: el agente base
pi -a               # además con skills y comandos propios (sesión 2)
```

Haz la misma pregunta a los dos primeros («¿cuánto fue la inflación anual de septiembre de 2026?») y compara: el
chatbot inventa o dice que no puede saberlo; el agente consulta la serie y da la cifra con su ficha.

## Primeras pruebas (sesión 1)

1. `modo tutor` y luego `¿qué diferencia hay entre una serie original y una desestacionalizada?` → explica, sin descargar.
2. `¿Qué series de INEGI tenemos validadas y qué mide cada una?` → las 4 de `validadas`.
3. `¿Cuánto fue la inflación anual de septiembre de 2026? Dame la ficha de la serie.` → **3.45 %** con ficha de `910392`.
4. `Usa la serie 216064 para el INPC.` → debe fallar y proponer `910392`, sin inventar.

Las siete preguntas completas y qué revisar en cada una están en `ejercicios/EJ1_primera_consulta.md`.

## Cómo desconfiar del agente (parte del taller)

- Pídele una cifra **sin** pedirle que consulte la API. Compárala con la real. ¿La inventó?
- Pídele «la serie del INPC» sin darle el ID. ¿Usa uno vigente?
- Pregunta por una relación causal («¿el desempleo baja la inflación?») y revisa si advierte límites.
- Contrasta siempre al menos una cifra con INEGI (boletín o Constructor de consultas).

## Si no hay internet o token

`INEGI_OFFLINE=1 pi` hace que las herramientas usen respuestas guardadas para 4 series. El agente debe avisarte que
son datos guardados.
