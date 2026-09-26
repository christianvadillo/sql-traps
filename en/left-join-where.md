# A WHERE on the right-hand table turns your LEFT JOIN back into an INNER JOIN

ON says how rows are glued together; WHERE decides which survive. With INNER JOIN the order doesn't matter; with LEFT JOIN, filtering in the WHERE on a column from the added table strips out exactly the unmatched rows the LEFT JOIN was there to keep.

## Where it shows up

Any time a LEFT JOIN is followed by a WHERE that mentions a column from the joined-in table. It's easy to write and the engine never warns you: it just quietly returns fewer rows than you asked for.

## The query with the trap

```sql
SELECT o.id, s.carrier
FROM orders o
LEFT JOIN shipments s ON s.order_id = o.id
WHERE s.carrier = 'DHL';
-- orders with no shipment have s.carrier = NULL,
-- and NULL = 'DHL' is NULL: the row is dropped as if this were an INNER JOIN
```

## The fix

```sql
SELECT o.id, s.carrier
FROM orders o
LEFT JOIN shipments s ON s.order_id = o.id
                     AND s.carrier = 'DHL';
-- or, if you genuinely want to exclude the rest:
WHERE s.carrier = 'DHL' OR s.carrier IS NULL
```

## Another way to fix it

```sql
SELECT o.id, s.carrier
FROM orders o
LEFT JOIN shipments s ON s.order_id = o.id
WHERE s.carrier = 'DHL' OR s.carrier IS NULL;
```

## Why

Any comparison with NULL evaluates to NULL, and a row whose WHERE evaluates to NULL isn't returned. That's not an edge case, it's the rule. When the condition is part of the matching criterion ("only DHL shipments, but still keep orders with no shipment"), it belongs in the ON. When you genuinely want to exclude rows from the final result, then it does go in the WHERE, with an added `OR column IS NULL` so you don't lose the ones that had no match to begin with.

## Minimal dataset to reproduce it

```sql
CREATE TABLE orders AS SELECT * FROM (VALUES (1), (2), (3)) AS t(id);
CREATE TABLE shipments AS SELECT * FROM (VALUES (1, 'DHL'), (2, 'FedEx')) AS t(order_id, carrier);
```

Check it: `python verify.py left-join-where`

## Related

- [Why does NOT IN return zero rows?](not-in-nulos.md)
- [Why doesn't WHERE find the customer who 'always' pays cash?](where-vs-having.md)
- [When do two time intervals actually overlap?](solape-de-intervalos.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/left-join-where
