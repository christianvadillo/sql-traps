# Why can't WHERE filter on a window function's result?

WHERE runs before the columns computed with OVER even exist. Filtering on a window function needs QUALIFY, or wrapping the query in a CTE and filtering from the outside.

## Where it shows up

Any filter on lag(), row_number(), sum() OVER (…) or another window function: 'the previous row less than 10 minutes ago', 'only the first of each group', 'only rows ranked first'.

## The query with the trap

```sql
SELECT card, moment,
       lag(moment) OVER (PARTITION BY card ORDER BY moment) AS previous
FROM validations
WHERE date_diff('minute', lag(moment) OVER (PARTITION BY card ORDER BY moment), moment) < 10;
-- error: a window function can't be called inside WHERE
```

## The fix

```sql
SELECT card, moment,
       lag(moment) OVER (PARTITION BY card ORDER BY moment) AS previous
FROM validations
QUALIFY date_diff('minute', previous, moment) < 10;
```

## Why

A query's real execution order is `FROM` → `WHERE` → `GROUP BY` → `HAVING` → *windows* → `QUALIFY` → `SELECT`. Window functions get computed after `WHERE`, so a `WHERE` can't reference `lag(...) OVER (...)`: the column doesn't exist yet at that point, and DuckDB rejects it with an error, not a wrong answer. `QUALIFY` is exactly `HAVING` for windows: it runs after they're computed and can use their result directly, including the alias you gave it in the `SELECT`. On engines without `QUALIFY` (nearly all except DuckDB, Snowflake and BigQuery) the equivalent is wrapping the query in a CTE and putting the filter in the outer query's `WHERE`, where the computed column already exists as an ordinary column.

## Minimal dataset to reproduce it

```sql
CREATE TABLE validations AS SELECT * FROM (VALUES
  ('T1', TIMESTAMP '2026-01-01 10:00:00'),
  ('T1', TIMESTAMP '2026-01-01 10:05:00'),
  ('T1', TIMESTAMP '2026-01-01 10:40:00'),
  ('T2', TIMESTAMP '2026-01-01 11:00:00')
) AS t(card, moment);
```

Check it: `python verify.py qualify-vs-where`

## Related

- [Why does the running balance repeat the exact same number on two different rows?](rango-vs-filas.md)
- [A WHERE on the right-hand table turns your LEFT JOIN back into an INNER JOIN](left-join-where.md)
- [Why does NOT IN return zero rows?](not-in-nulos.md)

Page with more context: https://casoabiertogame.com/traps/qualify-vs-where
