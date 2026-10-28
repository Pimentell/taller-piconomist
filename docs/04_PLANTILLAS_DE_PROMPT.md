# 04 · Plantillas de prompt: comandos propios

Una **plantilla de prompt** es un comando que tú defines: escribes `/serie 444884` y pi lo convierte en un mensaje
completo antes de enviárselo al agente. Sirve para las peticiones que repites siempre igual.

## Skill o plantilla

| | Skill | Plantilla de prompt |
|---|---|---|
| Qué es | Conocimiento de un método | Un mensaje prehecho con huecos |
| Quién decide usarla | El modelo, cuando la descripción coincide (o tú con `/skill:nombre`) | Tú, al escribir el comando |
| Dónde vive | `.agents/skills/<nombre>/SKILL.md` | `.pi/prompts/<nombre>.md` |
| Ejemplo | «cómo se deflacta con el INPC» | «valida y descarga la serie que te diga» |

Una plantilla puede pedir que se use una skill: `/investigar` invoca el flujo de `investigacion-economica`.

## Anatomía

Archivo `.pi/prompts/serie.md` → comando `/serie`:

```markdown
---
description: Identifica, valida y descarga una serie de INEGI por su ID
argument-hint: <ID de la serie>
---
Trabaja con la serie $1 de INEGI, en este orden:
1. Obtén su ficha y valídala con la skill validar-serie...
```

- El **nombre del archivo** es el nombre del comando.
- `description` aparece al autocompletar; `argument-hint` indica qué argumentos espera (`<obligatorio>`, `[opcional]`).
- Huecos: `$1`, `$2`… (un argumento cada uno), `$@` (todos los argumentos juntos), `${1:-valor}` (con valor por defecto).
  Las comillas agrupan: `/investigar "inflación y desempleo"` es un solo argumento.

## Reglas prácticas

- Las plantillas del repo se cargan **solo si confías en la carpeta**: arranca con `pi -a` (igual que las skills).
- Después de crear o editar una: `/reload`.
- Escribe el **orden de pasos** y los **puntos donde el agente debe detenerse a preguntarte**. Una plantilla es
  el lugar ideal para obligar a validar antes de calcular.

## Las dos que incluye el repo

| Comando | Qué hace |
|---|---|
| `/serie <ID>` | Ficha → validación → descarga → resumen con ficha final |
| `/investigar <pregunta>` | Reformula la pregunta, pide tu hipótesis **antes** de ver datos, propone series y espera tu confirmación |

Pruébalas: `/serie 444884` y `/investigar ¿la desocupación actual es atípica?`.

## Actividad (15 min): tu propio comando

Crea `.pi/prompts/inflacion.md` → `/inflacion <AAAA/MM>`, que:

1. valide la serie `910392` con la skill `validar-serie`;
2. calcule la inflación anual de ese mes con la skill `tasas-crecimiento`;
3. responda con la cifra, la ficha de la serie y una línea sobre cómo se calculó (mismo mes del año anterior).

Prueba: `/inflacion 2022/09` debe dar **8.70 %** y `/inflacion 2026/09`, **3.45 %**.

Lista de verificación:
- [ ] El comando aparece al escribir `/` (si no: `pi -a` y `/reload`)
- [ ] Usa el argumento (`$1`) donde corresponde
- [ ] El agente valida antes de calcular
- [ ] Reproduce la cifra de referencia
