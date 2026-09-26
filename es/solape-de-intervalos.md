# ¿Cuándo se solapan de verdad dos intervalos de tiempo?

Comparar sólo el inicio o sólo el fin no basta, y usar <= en vez de < convierte dos turnos que se tocan en un punto en un solape que no existe.

## Cuándo aparece

Coartadas, turnos, reservas, posiciones abiertas, ventanas de mantenimiento: cualquier pregunta de '¿estos dos periodos coinciden?'.

## La consulta con la trampa

```sql
SELECT a.persona, b.persona
FROM turnos a
JOIN turnos b
  ON a.persona <> b.persona
 AND a.desde <= b.hasta
 AND b.desde <= a.hasta;
-- con <=, dos turnos que se tocan en el mismo instante
-- (uno termina justo cuando el otro empieza) cuentan como solape
```

## La corrección

```sql
SELECT a.persona, b.persona
FROM turnos a
JOIN turnos b
  ON a.persona <> b.persona
 AND a.desde < b.hasta
 AND b.desde < a.hasta;
```

## Por qué

`a1 < b2 AND b1 < a2` cubre los cuatro solapes posibles (empieza dentro, acaba dentro, contiene, está contenido) sin necesidad de enumerarlos por separado; es el patrón que vale para siempre. La única decisión real es `<` frente a `<=`: con `<=`, un turno que termina a las 22:00 y otro que empieza a las 22:00 cuentan como solapados, aunque en la práctica no coincidieron ni un segundo. Cuál de los dos usar depende del dominio: dos reservas de sala que se tocan en el minuto exacto normalmente no chocan (`<` estricto); dos rangos de vigencia de precio donde el fin es inclusivo sí podrían necesitar `<=`. La regla no es 'usa siempre <': es 'decide primero si el instante límite pertenece a los dos intervalos o a ninguno'.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE turnos AS SELECT * FROM (VALUES
  ('Ana',  TIMESTAMP '2026-05-19 20:00', TIMESTAMP '2026-05-19 22:00'),
  ('Beto', TIMESTAMP '2026-05-19 22:00', TIMESTAMP '2026-05-20 00:00'),
  ('Caro', TIMESTAMP '2026-05-19 21:30', TIMESTAMP '2026-05-19 23:30')
) AS t(persona, desde, hasta);
```

Compruébalo: `python verify.py solape-de-intervalos`

## Relacionadas

- [¿Por qué un self-join siempre trae una fila de más?](self-join-trivial.md)
- [¿Por qué BETWEEN se come el último día del rango?](between-medianoche.md)
- [Un WHERE sobre la tabla derecha convierte tu LEFT JOIN en INNER](left-join-where.md)

Página con más contexto: https://caso-abierto.christianvadillo.workers.dev/trampas/solape-de-intervalos
