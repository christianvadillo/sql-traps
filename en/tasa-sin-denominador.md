# A rate needs a denominator

A raw count alone rewards whoever shows up most; a rate with no minimum sample rewards whoever shows up least. You need both at once.

## Where it shows up

Any ranking of "the best", "the most suspicious" or "the worst store": if the result is a proportion, the first question is what it's being divided by.

## The query with the trap

```sql
SELECT store, count(*) AS refunds
FROM refunds
GROUP BY store
ORDER BY refunds DESC;
-- the store with the most sales looks the worst, even if it refunds less than anyone
```

## The fix

```sql
SELECT o.store,
       count(r.order_id) * 1.0 / count(o.order_id) AS refund_rate,
       count(o.order_id) AS orders
FROM orders o
LEFT JOIN refunds r ON r.order_id = o.order_id
GROUP BY o.store
HAVING count(o.order_id) >= 30   -- without this, a store with 2 orders and
                                  -- 1 refund "wins" at 50%
ORDER BY refund_rate DESC;
```

## Why

The count points at whoever sells the most; a rate with no minimum points at whoever sells the least, because with few orders any extreme proportion is easy to hit. A `HAVING count(*) >= N` throws out samples too small for the rate to mean anything, and it's worth always comparing against the overall rate: if 5% of all orders get refunded, 12 out of 80 (15%) stands out; 1 out of 2 says nothing, even though it's "50%".

## Minimal dataset to reproduce it

```sql
CREATE TABLE orders AS
  SELECT i AS order_id, 'A' AS store FROM range(1, 41) t(i)
  UNION ALL
  SELECT i, 'B' FROM range(101, 103) t(i);
CREATE TABLE refunds AS SELECT * FROM (VALUES
  (1, 'A'), (2, 'A'), (3, 'A'), (4, 'A'), (101, 'B')
) AS t(order_id, store);
```

Check it: `python verify.py tasa-sin-denominador`

## Related

- [Why doesn't WHERE find the customer who 'always' pays cash?](where-vs-having.md)
- [The join that multiplies rows](fanout.md)
- [When do two time intervals actually overlap?](solape-de-intervalos.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/tasa-sin-denominador
