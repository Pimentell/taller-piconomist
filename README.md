# Taller: construye un agente de investigación económica

Un agente de IA que consulta datos oficiales de INEGI, valida lo que encuentra y te ayuda a investigar, y al que tú
le enseñas métodos de economía con **skills**. Se usa con [pi](https://pi.dev), un agente de código abierto para la
terminal. Todo lo que escribes aquí es **Python y Markdown**.

## Ruta por sesiones

| Cuándo | Qué | Dónde |
|---|---|---|
| **Antes de la sesión 1** | Instalar y comprobar: `python3 herramientas/doctor.py --red --modelo` | [`docs/00_PREPARACION.md`](docs/00_PREPARACION.md) |
| **Sesión 1 · Entender y arrancar** | Usar el agente base (`pi -a -ns`), hacerle las siete preguntas y revisarlas | [`docs/01_USAR_EL_AGENTE.md`](docs/01_USAR_EL_AGENTE.md), [`ejercicios/EJ1`](ejercicios/EJ1_primera_consulta.md) |
| **Entre sesiones** | Leer cómo se escribe una skill; pensar un método que sepas hacer a mano | [`docs/02_CREAR_SKILLS.md`](docs/02_CREAR_SKILLS.md) |
| **Sesión 2 · Enseñarle el oficio** | Con skill y sin skill (`pi -a`); escribir tu skill; crear comandos propios | [`ejercicios/EJ2`](ejercicios/EJ2_usar_una_skill.md), [`EJ3`](ejercicios/EJ3_tu_primera_skill_deflactar.md), [`docs/04_PLANTILLAS_DE_PROMPT.md`](docs/04_PLANTILLAS_DE_PROMPT.md) |
| **Extra / después** | Okun, mini-investigación, cómo se construye un agente por dentro | [`EJ4`](ejercicios/EJ4_skill_okun.md), [`EJ5`](ejercicios/EJ5_proyecto_libre.md), [`docs/03_CONSTRUIR_UN_AGENTE.md`](docs/03_CONSTRUIR_UN_AGENTE.md) |

## Qué hay en el repo

```
AGENTS.md                      personalidad y reglas del agente (pi lo lee solo)
.agents/skills/                skills: conocimiento que el agente carga cuando hace falta
  inegi-api/                   cómo consultar INEGI y sus trampas
  validar-serie/               verificar que una serie es la que crees
  investigacion-economica/     del planteamiento al informe reproducible
  tasas-crecimiento/           variaciones anuales y CAGR (con script de Python)
.pi/prompts/                   comandos propios: /serie <ID>, /investigar <pregunta>
.pi/settings.json              reintentos automáticos cuando el plan gratuito del modelo da «too many requests»
herramientas/inegi.py          cliente de INEGI (solo biblioteca estándar)
herramientas/doctor.py         revisa que tu equipo esté listo
herramientas/tests/            pruebas (corren sin internet)
datos/series_validadas.json    series ya identificadas y contrastadas, con cifras ancla
ejemplos/agente_minimo.py      un agente en ~80 líneas de Python
ejercicios/                    EJ1 (sesión 1), EJ2–EJ3 (sesión 2), EJ4–EJ5 (extra)
presentacion/                  diapositivas de las dos sesiones (ábrelas en el navegador; N muestra las notas)
plantilla-skill/               punto de partida para tus skills
fixtures/                      respuestas reales guardadas (modo sin internet)
investigacion/                 tu trabajo (se crea al usarlo; no se sube a git)
```

## Prueba rápida

```
python3 herramientas/doctor.py                            # qué falta en tu equipo
python3 -m unittest discover -s herramientas/tests        # debe terminar en OK
INEGI_OFFLINE=1 python3 herramientas/inegi.py ficha 910392  # sin token ni internet
```

## Aviso

Las cifras salen de INEGI y pueden revisarse con el tiempo. El agente puede equivocarse: **verifica** cada resultado
importante contra la fuente. Nunca pegues tu token en archivos del repo ni en mensajes con otras personas.
