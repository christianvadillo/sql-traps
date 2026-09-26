# Time zones: store UTC, show local

Grouping by day without deciding the time zone splits the same session across two days, and a clock change turns one day into 23 hours and the next into 25.

## Where it shows up

Any timestamped data that crosses time zones or a clock change: almost every system with users in more than one zone.

## The query with the trap

```sql
SELECT date_trunc('day', moment_utc) AS day
FROM sessions
GROUP BY day;
-- moment_utc carries no zone: date_trunc cuts on the UTC day.
-- In Mexico City (UTC−6) everything after 6 p.m.
-- lands on the next day
```

## The fix

```sql
SELECT date_trunc(
  'day',
  moment_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City'
) AS local_day
FROM sessions
GROUP BY local_day;
```

## Why

Both conversions are needed, in that order: the first says which instant that zone-less stored TIMESTAMP represents (read it as UTC), the second moves it to the clock over there. With only one conversion, the engine returns an instant and `date_trunc` cuts using the machine's own zone, so the same data gives a different day on every computer, and a clock change splits the same night's session across two dates.

## Minimal dataset to reproduce it

```sql
CREATE TABLE sessions AS SELECT * FROM (VALUES (TIMESTAMP '2024-01-02 03:00:00')) AS t(moment_utc);
```

Check it: `python verify.py husos-horarios`

## Related

- [Why does BETWEEN eat the last day of the range?](between-medianoche.md)
- [Survivorship bias lives in the JOIN](supervivencia.md)
- [Why does the running balance repeat the exact same number on two different rows?](rango-vs-filas.md)

Page with more context: https://caso-abierto.christianvadillo.workers.dev/traps/husos-horarios
