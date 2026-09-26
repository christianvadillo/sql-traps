# Why does BETWEEN eat the last day of the range?

BETWEEN 'a' AND 'b' on a TIMESTAMP turns 'b' into 'b 00:00:00'. Everything that happened after midnight on that day is left out, even though the whole day was supposed to count.

## Where it shows up

Any date filter using BETWEEN on a TIMESTAMP column (not DATE). It's why 'from the 1st to the 30th' almost never includes all of the 30th.

## The query with the trap

```sql
SELECT card, entry
FROM access_log
WHERE entry BETWEEN '2026-09-01' AND '2026-09-30';
-- '2026-09-30' is read as '2026-09-30 00:00:00':
-- the 10:47 pm entry on that same day is left out
```

## The fix

```sql
SELECT card, entry
FROM access_log
WHERE entry >= '2026-09-01'
  AND entry <  '2026-10-01';
```

## Why

`BETWEEN a AND b` on a `TIMESTAMP` isn't 'from day a to day b': it's 'from instant a to instant b', and a date-only literal like `'2026-09-30'` gets read as `'2026-09-30 00:00:00'`. That leaves out the 23 hours and 59 minutes that follow, right where this clue's break-in happened. The half-open range `>= start AND < exclusive_end` doesn't have that problem because it never depends on guessing what hour the next day starts: it just needs the first instant that no longer counts. The same rule applies to months and years: `< '2026-10-01'` includes all of September, no matter the hour.

## Minimal dataset to reproduce it

```sql
CREATE TABLE access_log AS SELECT * FROM (VALUES
  ('A-03', TIMESTAMP '2026-09-02 08:14'),
  ('B-17', TIMESTAMP '2026-09-12 19:02'),
  ('C-08', TIMESTAMP '2026-09-21 07:55'),
  ('A-03', TIMESTAMP '2026-09-29 18:40'),
  ('B-17', TIMESTAMP '2026-09-30 22:47'),
  ('C-08', TIMESTAMP '2026-10-01 06:10')
) AS t(card, entry);
```

Check it: `python verify.py between-medianoche`

## Related

- [Time zones: store UTC, show local](husos-horarios.md)
- [When do two time intervals actually overlap?](solape-de-intervalos.md)
- [Why does the running balance repeat the exact same number on two different rows?](rango-vs-filas.md)

Page with more context: https://casoabiertogame.com/traps/between-medianoche
