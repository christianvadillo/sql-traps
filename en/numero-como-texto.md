# Why does the biggest transfer of the month show up as $990?

If the amount was stored as text, ORDER BY compares it character by character: '9' comes before '75000' because the first character of '990' is bigger, no matter what digits follow.

## Where it shows up

Numeric columns imported from a CSV, an API or a form, that arrived as VARCHAR and nobody converted them. Sorting or comparing them as-is gives an order that looks random.

## The query with the trap

```sql
SELECT account, amount
FROM transfers
ORDER BY amount DESC
LIMIT 3;
-- amount is VARCHAR: '990' > '9500' > '870' because it's compared
-- character by character, and the $75,000 transfer never shows up
```

## The fix

```sql
SELECT account, amount
FROM transfers
ORDER BY CAST(amount AS BIGINT) DESC
LIMIT 3;
-- TRY_CAST instead of CAST if any row might carry non-numeric text
-- (a thousands comma, a blank cell): TRY_CAST gives NULL instead of blowing up the query
```

## Why

A `VARCHAR` sorts as text: it compares the first character, and only checks the second if they tie. `'990'` beats `'75000'` because `'9' > '7'`, and the comparison doesn't care that `'75000'` has more digits left over. `CAST(amount AS BIGINT)` converts before sorting, and there `75000` really is bigger than `990`. The difference between `CAST` and `TRY_CAST` matters on real data: `CAST` blows up the whole query if a single row carries `'12,000'` with a comma or an empty cell; `TRY_CAST` turns that one row into `NULL` and lets the rest through. Which one to use depends on whether you want to find out about the dirty data now or later.

## Minimal dataset to reproduce it

```sql
CREATE TABLE transfers AS SELECT * FROM (VALUES
  ('MX-1041', '1500'), ('MX-2208', '9500'), ('MX-0317', '75000'),
  ('MX-1190', '870'), ('MX-4402', '12000'), ('MX-3315', '8200'), ('MX-0928', '990')
) AS t(account, amount);
```

Check it: `python verify.py numero-como-texto`

## Related

- [Why doesn't LIKE find a name that's right there in the table?](like-mayusculas.md)
- [Why doesn't WHERE find the customer who 'always' pays cash?](where-vs-having.md)
- [Why does the running balance repeat the exact same number on two different rows?](rango-vs-filas.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/numero-como-texto
