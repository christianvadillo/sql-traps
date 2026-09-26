# Survivorship bias lives in the JOIN

Joining a history table against today's catalog measures who survived, not what actually happened: the ones that disappeared are exactly the ones carrying the bad news.

## Where it shows up

Historical studies over living catalogs: asset universes, active customers, products in range. More generally, any "how did X do" where X might no longer exist.

## The query with the trap

```sql
SELECT h.date, avg(h.return) AS avg_return
FROM history h
JOIN universe u ON u.symbol = h.symbol AND u.active
GROUP BY h.date;
-- symbols that went bankrupt or got delisted aren't in "universe.active",
-- so their bad track record never enters the average
```

## The fix

```sql
SELECT h.date, avg(h.return) AS avg_return
FROM history h
JOIN universe u
  ON u.symbol = h.symbol
 AND h.date >= u.added
 AND (u.removed IS NULL OR h.date <= u.removed)
GROUP BY h.date;
```

## Why

The "active" filter describes today's catalog, not the date of each row in the history table. The correct condition is temporal: a row counts if that symbol was part of the universe on that row's date. Use the `added`/`removed` field (or its equivalent) to reconstruct the universe as it was back then, not as it looks after the worst cases have already disappeared.

## Minimal dataset to reproduce it

```sql
CREATE TABLE history AS SELECT * FROM (VALUES
  (DATE '2020-02-01', 'AAA', 10.0),
  (DATE '2020-02-01', 'BBB', -50.0),
  (DATE '2020-08-01', 'AAA', 5.0)
) AS t(date, symbol, return);
CREATE TABLE universe AS SELECT * FROM (VALUES
  ('AAA', true, DATE '2020-01-01', NULL),
  ('BBB', false, DATE '2020-01-01', DATE '2020-06-01')
) AS t(symbol, active, added, removed);
```

Check it: `python verify.py supervivencia`

## Related

- [The join that multiplies rows](fanout.md)
- [Time zones: store UTC, show local](husos-horarios.md)
- [Why does a self-join always bring back one extra row?](self-join-trivial.md)

Page with more context: https://casoabiertogame.com/traps/supervivencia
