# EJ4 · Skill avanzada: ley de Okun (ejercicio extra, 50 min)

**Objetivo:** convertir un análisis completo en una skill repetible, con sus advertencias de interpretación.

## Pregunta

¿Cómo se relaciona el crecimiento anual del PIB real con el cambio anual de la tasa de desocupación en México?

## Datos

- PIB real trimestral: serie `736181` (desestacionalizada).
- Desocupación: serie `444884` (mensual, desestacionalizada). Promédiala por trimestre (solo trimestres con 3 meses).
- Trabaja con **variaciones contra el mismo trimestre del año anterior**: crecimiento del PIB en % y cambio de la
  desocupación en puntos porcentuales. Muestra: trimestres desde 2006/01.

## Especificación

`.agents/skills/okun/` con `SKILL.md` y `scripts/okun.py`, que estime por mínimos cuadrados:
`Δdesocupación = a + b · crecimiento PIB` e imprima n, b, error estándar de b y R².
Opciones: `--sin-covid` (excluye 2020/01–2021/04) y `--hasta 2019/04`.

## Cifras de referencia

| Muestra | n | Pendiente b | R² |
|---|---|---|---|
| Completa | 82 | −0.087 | 0.44 |
| Sin 2020/01–2021/04 | 74 | −0.148 | 0.52 |
| Hasta 2019/04 | 56 | −0.141 | 0.54 |

## La skill debe advertir

- Es una asociación, no causalidad.
- El periodo COVID cambia mucho el resultado: reporta con y sin él.
- Un coeficiente pequeño no prueba una causa (por ejemplo, que la informalidad amortigua la desocupación):
  eso sería una hipótesis nueva que requiere otros datos.

## Para pensar

- ¿Por qué usar variaciones y no niveles? (Pista: dos series con tendencia.)
- Prueba con el agente: `¿Cumple la ley de Okun en México?` ¿Qué responde con tu skill y sin ella?
