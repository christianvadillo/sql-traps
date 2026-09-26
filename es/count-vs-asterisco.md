# ¿Por qué COUNT(columna) da menos que COUNT(*)?

COUNT(*) cuenta filas. COUNT(columna) cuenta valores no nulos de esa columna. Si la columna admite NULL, los dos números casi nunca coinciden, y la diferencia no es un error: son los nulos.

## Cuándo aparece

Cualquier reporte que cuenta 'cuántas llamadas', 'cuántos clientes' o 'cuántos registros' usando COUNT sobre una columna en vez de COUNT(*). Pregunta habitual de entrevista porque la respuesta 'incorrecta' no da ningún error.

## La consulta con la trampa

```sql
SELECT COUNT(numero) AS llamadas
FROM llamadas;
-- la vecina jura que sonó 7 veces; esto devuelve 4:
-- las 3 llamadas con número oculto tienen numero = NULL
```

## La corrección

```sql
SELECT COUNT(*)      AS llamadas_totales,
       COUNT(numero) AS con_numero_visible
FROM llamadas;
```

## Por qué

`COUNT(*)` cuenta filas, sin mirar ninguna columna. `COUNT(columna)` cuenta cuántas de esas filas tienen un valor no nulo en esa columna concreta; salta cada `NULL`, como hace cualquier función de agregación salvo `COUNT(*)`. Ninguna de las dos consultas falla ni avisa: si alguien pide 'cuántas llamadas hubo' y usa `COUNT(numero)` porque `numero` es la columna que tiene delante, el número que sale es real, sólo que responde a otra pregunta. La regla de oficio: para 'cuántas filas hay', `COUNT(*)`; `COUNT(columna)` es para 'cuántas de esas filas tienen dato en esta columna', y esa es una pregunta distinta con una respuesta distinta.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE llamadas AS SELECT * FROM (VALUES
  ('23:02', '555-0142'), ('23:17', NULL), ('23:31', '555-0142'),
  ('23:48', NULL), ('00:05', '555-0199'), ('00:20', NULL), ('00:41', '555-0142')
) AS t(hora, numero);
```

Compruébalo: `python verify.py count-vs-asterisco`

## Relacionadas

- [¿Por qué NOT IN devuelve cero filas?](not-in-nulos.md)
- [¿Por qué el WHERE no encuentra a quien 'siempre' paga en efectivo?](where-vs-having.md)
- [Un WHERE sobre la tabla derecha convierte tu LEFT JOIN en INNER](left-join-where.md)

Página con más contexto: https://caso-abierto.christianvadillo.workers.dev/trampas/count-vs-asterisco
