# Why does NOT IN return zero rows?

NOT IN against a list with a single NULL throws out the whole query without a warning. It is the worst possible failure: it doesn't crash, it gives false confidence.

## Where it shows up

Any anti-join (what is missing, what has no match, what never got logged) written with NOT IN over a column that allows NULL. A classic SQL interview question, because it looks harmless.

## The query with the trap

```sql
SELECT name
FROM people
WHERE name NOT IN (
  SELECT name FROM alibis
);
-- alibis has one row with name NULL (an unsigned receipt):
-- the whole query returns zero rows, even though suspects with no alibi exist
```

## The fix

```sql
SELECT name
FROM people p
WHERE NOT EXISTS (
  SELECT 1 FROM alibis a WHERE a.name = p.name
);
-- or, filtering the NULL out of the list itself:
WHERE name NOT IN (
  SELECT name FROM alibis WHERE name IS NOT NULL
)
```

## Another way to fix it

```sql
SELECT name
FROM people
WHERE name NOT IN (
  SELECT name FROM alibis WHERE name IS NOT NULL
);
```

## Why

`x NOT IN (a, b, NULL)` is not a list with a gap in it: it's `x<>a AND x<>b AND x<>NULL`, and that last comparison evaluates to `NULL`, not true or false. A conjunction with a `NULL` in it never evaluates to true, so no row passes the filter, no matter how many names are genuinely missing. `NOT EXISTS` doesn't compare against the whole list at once: it asks row by row, so one NULL in the subquery doesn't poison the rest. The other fix is stripping the NULL before it reaches `NOT IN`, but that means remembering to do it every time; `NOT EXISTS` is the safe default.

## Minimal dataset to reproduce it

```sql
CREATE TABLE people AS SELECT * FROM (VALUES ('Ruiz'), ('Salas'), ('Ortega'), ('Bravo'), ('Mendez')) AS t(name);
CREATE TABLE alibis AS SELECT * FROM (VALUES ('Ruiz', 'bar camera'), ('Salas', 'her sister'), (NULL, 'unsigned receipt'), ('Bravo', 'night shift')) AS t(name, confirms);
```

Check it: `python verify.py not-in-nulos`

## Related

- [A WHERE on the right-hand table turns your LEFT JOIN back into an INNER JOIN](left-join-where.md)
- [Why does COUNT(column) give a smaller number than COUNT(*)?](count-vs-asterisco.md)
- [Why doesn't WHERE find the customer who 'always' pays cash?](where-vs-having.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/not-in-nulos
