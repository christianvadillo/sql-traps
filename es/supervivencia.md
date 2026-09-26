# El sesgo de supervivencia está en el JOIN

Unir un histórico contra el catálogo tal como está hoy mide quién sobrevivió, no lo que de verdad pasó: los que desaparecieron son justo los que traían la mala noticia.

## Cuándo aparece

Estudios históricos sobre catálogos vivos: universos de activos, clientes activos, productos en catálogo. En general, cualquier «cómo le fue a X» donde X puede haber dejado de existir.

## La consulta con la trampa

```sql
SELECT h.fecha, avg(h.retorno) AS retorno_medio
FROM historico h
JOIN universo u ON u.simbolo = h.simbolo AND u.activo
GROUP BY h.fecha;
-- los símbolos que quebraron o se deslistaron no están en "universo.activo",
-- así que su mal historial nunca entra al promedio
```

## La corrección

```sql
SELECT h.fecha, avg(h.retorno) AS retorno_medio
FROM historico h
JOIN universo u
  ON u.simbolo = h.simbolo
 AND h.fecha >= u.alta
 AND (u.baja IS NULL OR h.fecha <= u.baja)
GROUP BY h.fecha;
```

## Por qué

El filtro «activo» describe el catálogo hoy, no el día de cada fila del histórico. La condición correcta es temporal: la fila cuenta si ese símbolo formaba parte del universo en la fecha de esa fila, use el dato `alta`/`baja` (o el equivalente) para reconstruir el universo como era entonces, no como quedó después de que los peores casos ya hubieran desaparecido.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE historico AS SELECT * FROM (VALUES
  (DATE '2020-02-01', 'AAA', 10.0),
  (DATE '2020-02-01', 'BBB', -50.0),
  (DATE '2020-08-01', 'AAA', 5.0)
) AS t(fecha, simbolo, retorno);
CREATE TABLE universo AS SELECT * FROM (VALUES
  ('AAA', true, DATE '2020-01-01', NULL),
  ('BBB', false, DATE '2020-01-01', DATE '2020-06-01')
) AS t(simbolo, activo, alta, baja);
```

Compruébalo: `python verify.py supervivencia`

## Relacionadas

- [El join que multiplica filas](fanout.md)
- [Zonas horarias: guarda UTC, muestra local](husos-horarios.md)
- [¿Por qué un self-join siempre trae una fila de más?](self-join-trivial.md)

Página con más contexto: https://caso-abierto.christianvadillo.workers.dev/trampas/supervivencia
