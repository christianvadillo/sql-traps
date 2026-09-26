# The join that multiplies rows

Aggregating after a one-to-many JOIN duplicates every row on the "one" side once per matching row on the other side, and every sum computed afterward comes out inflated.

## Where it shows up

Any time you aggregate (sum, count, avg) after joining two tables. It's the mistake that produces reports whose numbers look believable and are wrong. Nobody double-checks them because they seem reasonable.

## The query with the trap

```sql
SELECT o.customer_id,
       sum(o.amount) AS billed,
       count(l.id)   AS lines
FROM orders o
JOIN lines l ON l.order_id = o.id
GROUP BY o.customer_id;
-- o.amount repeats once per line of the order:
-- an order of 100 with 3 lines adds up to 300
```

## The fix

```sql
SELECT o.customer_id,
       sum(o.amount) AS billed,
       sum(l.n)      AS lines
FROM orders o
JOIN (
  SELECT order_id, count(*) AS n
  FROM lines
  GROUP BY order_id
) l ON l.order_id = o.id
GROUP BY o.customer_id;
```

## Why

The question to ask after writing any JOIN is "how many rows do I expect out of this?". Compare the count before and after: `SELECT count(*) FROM orders` against `SELECT count(*) FROM orders JOIN lines ON …`. If the second number is bigger, the right-hand side has several rows per key, and any `sum()` or `avg()` computed afterward is inflated by exactly that proportion. The safe fix is to aggregate the table that multiplies rows in its own subquery or CTE, and join it already aggregated.

## Minimal dataset to reproduce it

```sql
CREATE TABLE orders AS SELECT * FROM (VALUES (1, 10, 100.0)) AS t(id, customer_id, amount);
CREATE TABLE lines AS SELECT * FROM (VALUES (1, 1), (2, 1), (3, 1)) AS t(id, order_id);
```

Check it: `python verify.py fanout`

## Related

- [Survivorship bias lives in the JOIN](supervivencia.md)
- [Why does a self-join always bring back one extra row?](self-join-trivial.md)
- [A rate needs a denominator](tasa-sin-denominador.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/fanout
