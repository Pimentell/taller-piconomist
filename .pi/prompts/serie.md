---
description: Identifica, valida y descarga una serie de INEGI por su ID
argument-hint: <ID de la serie>
---
Trabaja con la serie $1 de INEGI, en este orden:

1. Obtén su ficha y valídala con la skill validar-serie. Si no está en datos/series_validadas.json, dime qué haría
   falta para validarla y detente hasta que yo confirme.
2. Descárgala con `python3 herramientas/inegi.py serie $1`.
3. Resume: nombre completo, unidad, frecuencia, si es original o desestacionalizada, fuente, última actualización,
   rango de fechas y los tres últimos datos.
4. Cierra con la ficha en el formato de la skill validar-serie.
