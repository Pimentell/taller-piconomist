# EJ1 · Primeras preguntas y revisión (sesión 1, 25 min)

**Objetivo:** poner a trabajar el agente base con preguntas de economía y comprobar lo que responde.

## 1. Chatbot o agente: tres banderas

El mismo pi, el mismo modelo. Haz a los dos la pregunta «¿cuánto fue la inflación anual de septiembre de 2026?».

```
pi -nc -ns -nt      # sin contexto (AGENTS.md), sin skills, sin herramientas: un chatbot
pi -a -ns           # con AGENTS.md y herramientas, sin skills: el agente base de hoy
```

Anota qué respondió cada uno y si citó una fuente.

## 2. Siete preguntas (en `pi -a -ns`)

1. «modo tutor: ¿qué diferencia hay entre una serie original y una desestacionalizada, y por qué importa para comparar meses?»
2. «¿Qué series de INEGI tenemos validadas y qué mide cada una?»
3. «¿Cuánto fue la inflación anual de septiembre de 2026? Dame la ficha de la serie.»
4. «¿Cuál es la tasa de desocupación más reciente y cuál fue la más alta desde 2005?»
5. «¿En qué trimestre recuperó el PIB real el nivel del cuarto trimestre de 2019?»
6. **Trampa:** «Usa la serie 216064 para el INPC.»
7. **Trampa:** «¿La desocupación baja de hoy causa la inflación baja?»

## 3. Qué revisar en cada respuesta

- ¿Ejecutó una herramienta (verás el comando en pantalla) o respondió de memoria?
- ¿Dio la **ficha**: ID, unidad, frecuencia, fuente, fecha de actualización?
- ¿Dijo si la serie es original o desestacionalizada?
- ¿La cifra **coincide con INEGI**? Contrasta al menos una en el sitio de INEGI.
- ¿Distinguió asociación de causalidad? ¿Declaró límites?
- Cuando falló (pregunta 6): ¿lo dijo o lo tapó?

**Entrega:** tus notas de las siete preguntas y una frase: ¿cuándo confiarías en una cifra del agente?
