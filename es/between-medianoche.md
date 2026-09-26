# ¿Por qué BETWEEN se come el último día del rango?

BETWEEN 'a' AND 'b' sobre un TIMESTAMP convierte 'b' en 'b 00:00:00'. Todo lo que pasó después de la medianoche de ese día queda fuera, aunque el día entero debía contarse.

## Cuándo aparece

Cualquier filtro de fechas con BETWEEN sobre una columna TIMESTAMP (no DATE). Es la razón por la que 'del 1 al 30' casi nunca incluye el 30 entero.

## La consulta con la trampa

```sql
SELECT tarjeta, entrada
FROM accesos
WHERE entrada BETWEEN '2026-09-01' AND '2026-09-30';
-- '2026-09-30' se interpreta como '2026-09-30 00:00:00':
-- la entrada de las 22:47 de ese mismo día queda fuera
```

## La corrección

```sql
SELECT tarjeta, entrada
FROM accesos
WHERE entrada >= '2026-09-01'
  AND entrada <  '2026-10-01';
```

## Por qué

`BETWEEN a AND b` sobre un `TIMESTAMP` no es 'del día a al día b': es 'del instante a al instante b', y un literal de sólo fecha como `'2026-09-30'` se convierte en `'2026-09-30 00:00:00'`. Eso deja fuera las 23 horas y 59 minutos que le siguen, justo donde ocurrió el robo de esta pista. El rango semiabierto `>= inicio AND < fin_exclusivo` no tiene ese problema porque nunca depende de adivinar a qué hora empieza el día siguiente: basta con poner el primer instante que ya NO cuenta. La misma regla vale para meses y años: `< '2026-10-01'` incluye todo septiembre completo, sin importar la hora.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE accesos AS SELECT * FROM (VALUES
  ('A-03', TIMESTAMP '2026-09-02 08:14'),
  ('B-17', TIMESTAMP '2026-09-12 19:02'),
  ('C-08', TIMESTAMP '2026-09-21 07:55'),
  ('A-03', TIMESTAMP '2026-09-29 18:40'),
  ('B-17', TIMESTAMP '2026-09-30 22:47'),
  ('C-08', TIMESTAMP '2026-10-01 06:10')
) AS t(tarjeta, entrada);
```

Compruébalo: `python verify.py between-medianoche`

## Relacionadas

- [Zonas horarias: guarda UTC, muestra local](husos-horarios.md)
- [¿Cuándo se solapan de verdad dos intervalos de tiempo?](solape-de-intervalos.md)
- [¿Por qué el saldo acumulado repite el mismo número en dos filas distintas?](rango-vs-filas.md)

Página con más contexto: https://casoabiertogame.com/trampas/between-medianoche
