# Why does the running balance repeat the exact same number on two different rows?

sum(...) OVER (ORDER BY date) with no explicit frame defaults to RANGE: it groups every row with the same date into one block, and all of them show the same running total.

## Where it shows up

Any running balance, cumulative total or ranking computed with a window function when the ORDER BY column has ties (two transactions the same day, two sales at the same hour).

## The query with the trap

```sql
SELECT date, amount,
       sum(amount) OVER (ORDER BY date) AS balance
FROM transactions;
-- two entries on the same day fall into the same RANGE:
-- both show the balance after adding both of them, neither shows the balance in between
```

## The fix

```sql
SELECT date, amount,
       sum(amount) OVER (
         ORDER BY date
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS balance
FROM transactions;
```

## Why

When a window function has an `ORDER BY` but no explicit frame, the engine defaults to `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, and `RANGE` groups by *value*, not by row: every row sharing the same `ORDER BY` value lands at the same point in the frame, so all of them see the same sum, the one after adding all of them. `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` moves row by row regardless of ties: the first of two same-day entries sees the balance before the second is added, and the second sees the balance with both. The rule of thumb: if the word is 'running balance' or 'cumulative through this row', you almost always want `ROWS`, not the `RANGE` you get by default without asking for it.

## Minimal dataset to reproduce it

```sql
CREATE TABLE transactions AS SELECT * FROM (VALUES
  (DATE '2026-04-01', 100.0),
  (DATE '2026-04-02', 50.0),
  (DATE '2026-04-02', 30.0),
  (DATE '2026-04-03', 20.0)
) AS t(date, amount);
```

Check it: `python verify.py rango-vs-filas`

## Related

- [Why can't WHERE filter on a window function's result?](qualify-vs-where.md)
- [Time zones: store UTC, show local](husos-horarios.md)
- [Why does the biggest transfer of the month show up as $990?](numero-como-texto.md)

Page with more context: https://casoabiertogame.com/traps/rango-vs-filas
