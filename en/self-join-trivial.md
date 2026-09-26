# Why does a self-join always bring back one extra row?

Joining a table against itself without excluding the row-against-itself match means every record pairs up with its own copy: a row that says nothing, but still counts.

## Where it shows up

Comparing rows of the same table against each other: who matched with whom, duplicates, pairs, overlaps. Any self-join with no condition that discards the trivial pairing.

## The query with the trap

```sql
SELECT o.member, o.checkin, v.member AS matched_with
FROM stays o
JOIN stays v
  ON o.room = v.room
 AND o.checkin < v.checkout
 AND v.checkin < o.checkout;
-- every stay overlaps with itself (o.member = v.member on two rows):
-- those rows say nothing, and they inflate any count computed afterward
```

## The fix

```sql
SELECT o.member, o.checkin, v.member AS matched_with
FROM stays o
JOIN stays v
  ON o.room = v.room
 AND o.id <> v.id
 AND o.checkin < v.checkout
 AND v.checkin < o.checkout;
```

## Why

Without a condition comparing one copy's key against the other's, every row in the table always finds a match in itself: same room, same time window, a perfect overlap because it's the same stay. `o.id <> v.id` (or the equivalent primary-key condition) removes exactly those rows and only those. The mistake is easy to miss because the trivial row often looks reasonable at a glance, someone 'matched with themselves', and it only shows up once the result has more rows than expected, or a `count(*)` downstream comes out inflated by exactly one per original row.

## Minimal dataset to reproduce it

```sql
CREATE TABLE stays AS SELECT * FROM (VALUES
  (1, 'A', 'Reservado 3', TIMESTAMP '2026-06-02 23:10', TIMESTAMP '2026-06-02 23:55'),
  (2, 'B', 'Reservado 3', TIMESTAMP '2026-06-02 23:25', TIMESTAMP '2026-06-02 23:50')
) AS t(id, member, room, checkin, checkout);
```

Check it: `python verify.py self-join-trivial`

## Related

- [When do two time intervals actually overlap?](solape-de-intervalos.md)
- [The join that multiplies rows](fanout.md)
- [Survivorship bias lives in the JOIN](supervivencia.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/self-join-trivial
