# 02 · Cómo agregarle skills al agente

Una **skill** es conocimiento de un método, escrito para que el agente lo aplique cuando haga falta. Tú ya sabes
deflactar una serie o interpretar la ley de Okun: aquí se lo enseñas al agente una vez, y lo usa siempre igual.

## Anatomía

```
.agents/skills/
└── mi-skill/
    ├── SKILL.md          ← obligatorio
    └── scripts/
        └── mi_script.py  ← opcional: el cálculo en Python
```

`SKILL.md` empieza con un encabezado (frontmatter) y sigue con instrucciones en Markdown:

```markdown
---
name: deflactar-inpc
description: Convierte montos entre fechas con el INPC. Úsala cuando se pida expresar pesos corrientes en pesos constantes o comparar montos de años distintos.
---

# Deflactar con el INPC
...instrucciones, comando exacto, reglas, cifras de referencia...
```

Reglas del formato:
- `name`: minúsculas, números y guiones, hasta 64 caracteres, **igual al nombre de la carpeta**.
- `description`: hasta 1024 caracteres. **Sin descripción la skill no carga.**

## La descripción es lo más importante

pi solo le muestra al modelo el `name` y la `description`. El contenido completo se lee **cuando la descripción
coincide con la tarea**. Una buena descripción dice **qué hace** y **cuándo usarla**, con las palabras que usaría
una persona: «inflación anual», «pesos constantes», «tasa de crecimiento».

| Mala | Buena |
|---|---|
| «Cosas de precios.» | «Convierte montos entre fechas con el INPC. Úsala cuando se pida pesos constantes o comparar montos de años distintos.» |

## Qué poner en el cuerpo

1. **Cuándo aplica** y cuándo no.
2. **El comando exacto** a correr (el agente debe copiarlo, no inventarlo).
3. **Reglas del método** que un economista cuida (misma fecha base, original vs. desestacionalizada, unidades).
4. **Cifras de referencia** (anclas): resultados que el método debe reproducir. Es tu prueba.
5. **Errores comunes** y cómo reconocerlos.

Si hay cálculo, ponlo en un script de Python (`scripts/`). El agente ejecuta el script en vez de escribir la fórmula cada
vez: el resultado es repetible. El script debe tener `--ayuda` (argparse), validar sus entradas y fallar con un mensaje claro.

## El ciclo de trabajo

1. Copia `plantilla-skill/SKILL.md` a `.agents/skills/<tu-nombre>/SKILL.md` y edítala.
2. En pi: `/reload`.
3. Prueba **con** la skill: `/skill:<tu-nombre> <la tarea>`.
4. Prueba **sin** la skill: sal de pi y corre `pi -ns` (desactiva skills) con el mismo prompt. ¿Qué cambió?
5. Verifica con la cifra de referencia. Si no coincide: ¿error en la skill, en los datos o en cómo la usó el agente?
6. Ajusta la **descripción** si el agente no la elige solo; ajusta el **cuerpo** si la usa mal.

## Prueba de la skill (lista de verificación)

- [ ] Se activa sola con una pregunta natural (sin `/skill:`)
- [ ] El comando que da es exactamente el que está en la skill
- [ ] Reproduce la cifra de referencia
- [ ] Falla con un mensaje claro si el dato no existe
- [ ] No inventa nada que la skill no diga

## Ideas de skills para economistas

Deflactar con el INPC · Okun · Curva de Phillips (con la advertencia de series con tendencia) · Tasa real de interés ·
Tipo de cambio real · Desestacionalizar (cuándo sí y cuándo no) · Estilo de gráficas · Redacción de resúmenes
ejecutivos · Glosario de indicadores de INEGI.

Los ejercicios `ejercicios/EJ3` y `EJ4` te guían en dos de ellas.
