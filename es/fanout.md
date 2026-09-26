# El join que multiplica filas

Agregar después de un JOIN uno-a-muchos duplica cada fila del lado «uno» tantas veces como filas tenga enfrente, y toda suma posterior sale inflada.

## Cuándo aparece

Siempre que agregues (sum, count, avg) después de unir dos tablas. Es el error que produce informes con números creíbles y falsos: nadie los revisa porque parecen razonables.

## La consulta con la trampa

```sql
SELECT p.cliente_id,
       sum(p.importe) AS facturado,
       count(l.id)    AS lineas
FROM pedidos p
JOIN lineas l ON l.pedido_id = p.id
GROUP BY p.cliente_id;
-- p.importe se repite una vez por cada línea del pedido:
-- un pedido de 100 con 3 líneas suma 300
```

## La corrección

```sql
SELECT p.cliente_id,
       sum(p.importe) AS facturado,
       sum(l.n)       AS lineas
FROM pedidos p
JOIN (
  SELECT pedido_id, count(*) AS n
  FROM lineas
  GROUP BY pedido_id
) l ON l.pedido_id = p.id
GROUP BY p.cliente_id;
```

## Por qué

La pregunta que hay que hacerse después de escribir cualquier JOIN es «¿cuántas filas espero que salgan?». Compara el conteo antes y después: `SELECT count(*) FROM pedidos` contra `SELECT count(*) FROM pedidos JOIN lineas ON …`. Si el segundo número es mayor, el lado derecho tiene varias filas por clave y cualquier `sum()` o `avg()` posterior queda inflado exactamente en esa proporción. Lo seguro es agregar la tabla que multiplica filas en una subconsulta o CTE propio, y unir ya agregada.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE pedidos AS SELECT * FROM (VALUES (1, 10, 100.0)) AS t(id, cliente_id, importe);
CREATE TABLE lineas AS SELECT * FROM (VALUES (1, 1), (2, 1), (3, 1)) AS t(id, pedido_id);
```

Compruébalo: `python verify.py fanout`

## Relacionadas

- [El sesgo de supervivencia está en el JOIN](supervivencia.md)
- [¿Por qué un self-join siempre trae una fila de más?](self-join-trivial.md)
- [Una tasa sin denominador no significa nada](tasa-sin-denominador.md)

Página con más contexto: https://caso-abierto.christianvadillo.workers.dev/trampas/fanout
