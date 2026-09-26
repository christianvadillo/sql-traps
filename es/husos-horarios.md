# Zonas horarias: guarda UTC, muestra local

Agrupar por día sin decidir el huso horario reparte la misma sesión entre dos días, y el cambio de hora crea un día de 23 horas y otro de 25.

## Cuándo aparece

Cualquier dato con marca de tiempo que cruce husos horarios o un cambio de hora: casi todos los sistemas con usuarios en más de una zona.

## La consulta con la trampa

```sql
SELECT date_trunc('day', momento_utc) AS dia
FROM sesiones
GROUP BY dia;
-- momento_utc no lleva huso: date_trunc corta en el día UTC.
-- En Ciudad de México (UTC−6) todo lo que pasa después de las
-- 18:00 se apunta al día siguiente
```

## La corrección

```sql
SELECT date_trunc(
  'day',
  momento_utc AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City'
) AS dia_local
FROM sesiones
GROUP BY dia_local;
```

## Por qué

Hacen falta las dos conversiones y en ese orden: la primera dice qué instante representa ese TIMESTAMP guardado sin huso (interpretarlo como UTC), la segunda lo traduce al reloj de allí. Con una sola conversión, el motor devuelve un instante y el `date_trunc` corta usando el huso de la máquina, y el mismo dato da un día distinto en cada ordenador, y un cambio de hora reparte la misma sesión de la noche entre dos fechas.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE sesiones AS SELECT * FROM (VALUES (TIMESTAMP '2024-01-02 03:00:00')) AS t(momento_utc);
```

Compruébalo: `python verify.py husos-horarios`

## Relacionadas

- [¿Por qué BETWEEN se come el último día del rango?](between-medianoche.md)
- [El sesgo de supervivencia está en el JOIN](supervivencia.md)
- [¿Por qué el saldo acumulado repite el mismo número en dos filas distintas?](rango-vs-filas.md)

Página con más contexto: https://casoabiertogame.com/trampas/husos-horarios
