# Why doesn't WHERE find the customer who 'always' pays cash?

Filtering in the WHERE before grouping answers a different question: it counts who paid cash several times, it doesn't check they ALWAYS did. 'Always' describes the whole group, and that belongs in HAVING.

## Where it shows up

Any question with 'always', 'never' or 'every time': the whole group needs to reach GROUP BY before you decide whether it follows the rule.

## The query with the trap

```sql
SELECT customer
FROM payments
WHERE method = 'cash'
GROUP BY customer
HAVING count(*) >= 3;
-- this finds anyone who paid cash 3 times or more,
-- even if they also paid by card: the WHERE already dropped that row
```

## The fix

```sql
SELECT customer
FROM payments
GROUP BY customer
HAVING count(*) >= 3
   AND count(*) FILTER (WHERE method <> 'cash') = 0;
```

## Why

`WHERE method = 'cash'` runs before `GROUP BY`: it drops the card rows before the group even forms, so `HAVING count(*) >= 3` only sees the cash rows that survived and never finds out that customer also paid by card at some point. What that query really answers is 'did they pay cash at least three times', not 'did they always pay cash'. To ask about the whole group, the whole group needs to reach `GROUP BY`: drop the `WHERE` and use `count(*) FILTER (WHERE method <> 'cash') = 0` to require that no row breaks the rule, together with `count(*) >= 3` to require a minimum amount of data. `FILTER` counts conditionally without needing to delete rows before the group is complete.

## Minimal dataset to reproduce it

```sql
CREATE TABLE payments AS SELECT * FROM (VALUES
  ('X', 'cash'), ('X', 'cash'), ('X', 'cash'),
  ('Y', 'cash'), ('Y', 'cash'), ('Y', 'cash'), ('Y', 'card'),
  ('Z', 'cash'), ('Z', 'cash')
) AS t(customer, method);
```

Check it: `python verify.py where-vs-having`

## Related

- [A rate needs a denominator](tasa-sin-denominador.md)
- [Why does COUNT(column) give a smaller number than COUNT(*)?](count-vs-asterisco.md)
- [Why does NOT IN return zero rows?](not-in-nulos.md)

Page with more context: https://casoabiertogame.com/traps/where-vs-having
