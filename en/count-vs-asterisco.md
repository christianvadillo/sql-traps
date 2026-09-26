# Why does COUNT(column) give a smaller number than COUNT(*)?

COUNT(*) counts rows. COUNT(column) counts that column's non-null values. If the column allows NULL, the two numbers almost never match, and the gap isn't a bug: it's the nulls.

## Where it shows up

Any report that counts 'how many calls', 'how many customers' or 'how many records' using COUNT on a column instead of COUNT(*). A common interview question, because the 'wrong' answer never raises an error.

## The query with the trap

```sql
SELECT COUNT(number) AS calls
FROM calls;
-- the neighbor swears the phone rang 7 times; this returns 4:
-- the 3 calls with a hidden caller ID have number = NULL
```

## The fix

```sql
SELECT COUNT(*)      AS total_calls,
       COUNT(number) AS with_visible_number
FROM calls;
```

## Why

`COUNT(*)` counts rows, without looking at any column. `COUNT(column)` counts how many of those rows have a non-null value in that specific column; it skips every `NULL`, the way any aggregate does except `COUNT(*)`. Neither query fails or warns: if someone asks 'how many calls were there' and reaches for `COUNT(number)` because `number` is the column in front of them, the number that comes out is real, it just answers a different question. The rule of thumb: for 'how many rows are there', use `COUNT(*)`; `COUNT(column)` is for 'how many of those rows have data in this column', and that's a different question with a different answer.

## Minimal dataset to reproduce it

```sql
CREATE TABLE calls AS SELECT * FROM (VALUES
  ('23:02', '555-0142'), ('23:17', NULL), ('23:31', '555-0142'),
  ('23:48', NULL), ('00:05', '555-0199'), ('00:20', NULL), ('00:41', '555-0142')
) AS t(hour, number);
```

Check it: `python verify.py count-vs-asterisco`

## Related

- [Why does NOT IN return zero rows?](not-in-nulos.md)
- [Why doesn't WHERE find the customer who 'always' pays cash?](where-vs-having.md)
- [A WHERE on the right-hand table turns your LEFT JOIN back into an INNER JOIN](left-join-where.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/count-vs-asterisco
