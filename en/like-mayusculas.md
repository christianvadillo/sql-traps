# Why doesn't LIKE find a name that's right there in the table?

LIKE compares character by character and is case-sensitive. If the real data comes in uppercase, lowercase or without accents, a well-written pattern misses rows sitting right in front of it.

## Where it shows up

Free-text search over names, addresses or any field people type by hand: case and accents are never consistent across systems.

## The query with the trap

```sql
SELECT *
FROM guests
WHERE name LIKE '%Vela%';
-- the front desk says Vela stayed 3 nights; this only finds 1:
-- 'VELA, ANDRES' and 'vela andres' don't match '%Vela%'
```

## The fix

```sql
SELECT *
FROM guests
WHERE name ILIKE '%vela%';
```

## Why

`LIKE` is case-sensitive in DuckDB (like in most engines, unless the column uses a special collation): `'VELA, ANDRES' LIKE '%Vela%'` is false, letter for letter, not an approximation. `ILIKE` runs the same comparison while ignoring case. There's a sibling problem `ILIKE` doesn't fix: accents. `'andres' ILIKE '%andrés%'` is also false, because the engine cares about the accent mark as much as the case; that needs normalizing both sides with `strip_accents()` before comparing. Neither engine warns you when a pattern finds nothing: zero rows reads as 'nobody matches', not as 'you searched wrong'.

## Minimal dataset to reproduce it

```sql
CREATE TABLE guests AS SELECT * FROM (VALUES
  ('Ibarra Thomas', 102, DATE '2026-03-01'),
  ('Vela Andrew', 204, DATE '2026-03-02'),
  ('Nava Lucy', 311, DATE '2026-03-05'),
  ('VELA, ANDREW', 311, DATE '2026-03-09'),
  ('vela andrew', 204, DATE '2026-03-15')
) AS t(name, room, arrival);
```

Check it: `python verify.py like-mayusculas`

## Related

- [Why does the biggest transfer of the month show up as $990?](numero-como-texto.md)
- [Why does NOT IN return zero rows?](not-in-nulos.md)
- [Why does COUNT(column) give a smaller number than COUNT(*)?](count-vs-asterisco.md)

Page with more context: https://casoabiertogame.com/traps/like-mayusculas
