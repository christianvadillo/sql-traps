# When do two time intervals actually overlap?

Comparing only the start or only the end isn't enough, and using <= instead of < turns two shifts that merely touch at one point into an overlap that isn't real.

## Where it shows up

Alibis, shifts, bookings, open positions, maintenance windows: any 'do these two periods coincide' question.

## The query with the trap

```sql
SELECT a.person, b.person
FROM shifts a
JOIN shifts b
  ON a.person <> b.person
 AND a.starts <= b.ends
 AND b.starts <= a.ends;
-- with <=, two shifts that merely touch at the same instant
-- (one ends exactly when the other begins) count as overlapping
```

## The fix

```sql
SELECT a.person, b.person
FROM shifts a
JOIN shifts b
  ON a.person <> b.person
 AND a.starts < b.ends
 AND b.starts < a.ends;
```

## Why

`a1 < b2 AND b1 < a2` covers all four possible overlaps (starts inside, ends inside, contains, is contained) without enumerating them one by one; it's the pattern that always holds. The one real decision is `<` versus `<=`: with `<=`, a shift ending at 10 pm and another starting at 10 pm count as overlapping, even though in practice they didn't coincide for a single second. Which one to use depends on the domain: two room bookings that touch at the exact minute usually don't clash (strict `<`); two price-validity date ranges where the end is inclusive might genuinely need `<=`. The rule isn't 'always use <': it's 'decide first whether the boundary instant belongs to both intervals or to neither'.

## Minimal dataset to reproduce it

```sql
CREATE TABLE shifts AS SELECT * FROM (VALUES
  ('Ana',  TIMESTAMP '2026-05-19 20:00', TIMESTAMP '2026-05-19 22:00'),
  ('Beto', TIMESTAMP '2026-05-19 22:00', TIMESTAMP '2026-05-20 00:00'),
  ('Caro', TIMESTAMP '2026-05-19 21:30', TIMESTAMP '2026-05-19 23:30')
) AS t(person, starts, ends);
```

Check it: `python verify.py solape-de-intervalos`

## Related

- [Why does a self-join always bring back one extra row?](self-join-trivial.md)
- [Why does BETWEEN eat the last day of the range?](between-medianoche.md)
- [A WHERE on the right-hand table turns your LEFT JOIN back into an INNER JOIN](left-join-where.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/solape-de-intervalos
