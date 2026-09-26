# ¿Por qué WHERE no puede filtrar el resultado de una window function?

El WHERE se evalúa antes de que existan las columnas calculadas con OVER. Para filtrar por una window function hace falta QUALIFY, o envolver la consulta en un CTE y filtrar desde fuera.

## Cuándo aparece

Cualquier filtro sobre lag(), row_number(), sum() OVER (…) u otra window function: 'la fila anterior a menos de 10 minutos', 'sólo la primera de cada grupo', 'sólo las filas con ranking 1'.

## La consulta con la trampa

```sql
SELECT tarjeta, momento,
       lag(momento) OVER (PARTITION BY tarjeta ORDER BY momento) AS previo
FROM validaciones
WHERE date_diff('minute', lag(momento) OVER (PARTITION BY tarjeta ORDER BY momento), momento) < 10;
-- error: no se puede llamar a una window function dentro del WHERE
```

## La corrección

```sql
SELECT tarjeta, momento,
       lag(momento) OVER (PARTITION BY tarjeta ORDER BY momento) AS previo
FROM validaciones
QUALIFY date_diff('minute', previo, momento) < 10;
```

## Por qué

El orden real de ejecución de una consulta es `FROM` → `WHERE` → `GROUP BY` → `HAVING` → *ventanas* → `QUALIFY` → `SELECT`. Las window functions se calculan después del `WHERE`, así que un `WHERE` no puede referirse a `lag(...) OVER (...)`: la columna todavía no existe en ese punto, y DuckDB lo rechaza con un error, no con un resultado equivocado. `QUALIFY` es exactamente el `HAVING` de las ventanas: corre después de calcularlas y puede usar su resultado directamente, incluso el alias que le diste en el `SELECT`. En motores sin `QUALIFY` (casi todos salvo DuckDB, Snowflake y BigQuery) el equivalente es envolver la consulta en un CTE y poner el filtro en el `WHERE` de la consulta exterior, donde la columna calculada ya existe como una columna normal.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE validaciones AS SELECT * FROM (VALUES
  ('T1', TIMESTAMP '2026-01-01 10:00:00'),
  ('T1', TIMESTAMP '2026-01-01 10:05:00'),
  ('T1', TIMESTAMP '2026-01-01 10:40:00'),
  ('T2', TIMESTAMP '2026-01-01 11:00:00')
) AS t(tarjeta, momento);
```

Compruébalo: `python verify.py qualify-vs-where`

## Relacionadas

- [¿Por qué el saldo acumulado repite el mismo número en dos filas distintas?](rango-vs-filas.md)
- [Un WHERE sobre la tabla derecha convierte tu LEFT JOIN en INNER](left-join-where.md)
- [¿Por qué NOT IN devuelve cero filas?](not-in-nulos.md)

Página con más contexto: https://casoabiertogame.com/trampas/qualify-vs-where
