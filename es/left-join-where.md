# Un WHERE sobre la tabla derecha convierte tu LEFT JOIN en INNER

El ON dice cómo se pegan las filas; el WHERE decide cuáles sobreviven. Con INNER JOIN da igual el orden; con LEFT JOIN, filtrar en el WHERE sobre una columna de la tabla de la derecha borra justo las filas sin pareja que el LEFT JOIN pretendía conservar.

## Cuándo aparece

Cada vez que un LEFT JOIN va seguido de un WHERE que menciona una columna de la tabla añadida. Es fácil de escribir y el motor no avisa: simplemente devuelve menos filas de las que pediste.

## La consulta con la trampa

```sql
SELECT p.id, e.transportista
FROM pedidos p
LEFT JOIN envios e ON e.pedido_id = p.id
WHERE e.transportista = 'DHL';
-- los pedidos sin envío tienen e.transportista NULL,
-- y NULL = 'DHL' da NULL: la fila se descarta como si fuera INNER JOIN
```

## La corrección

```sql
SELECT p.id, e.transportista
FROM pedidos p
LEFT JOIN envios e ON e.pedido_id = p.id
                  AND e.transportista = 'DHL';
-- o, si de verdad quieres excluir el resto:
WHERE e.transportista = 'DHL' OR e.transportista IS NULL
```

## Otra forma de corregirla

```sql
SELECT p.id, e.transportista
FROM pedidos p
LEFT JOIN envios e ON e.pedido_id = p.id
WHERE e.transportista = 'DHL' OR e.transportista IS NULL;
```

## Por qué

Cualquier comparación con NULL da NULL, y una fila cuyo WHERE evalúa a NULL no se devuelve. No es un caso raro, es la regla. Cuando la condición pertenece al criterio de emparejamiento («sólo los envíos de DHL, pero conserva igual los pedidos sin envío»), va en el ON. Cuando de verdad quieres excluir filas del resultado final, entonces sí en el WHERE, añadiendo el `OR columna IS NULL` para no perder las que no tenían pareja.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE pedidos AS SELECT * FROM (VALUES (1), (2), (3)) AS t(id);
CREATE TABLE envios AS SELECT * FROM (VALUES (1, 'DHL'), (2, 'FedEx')) AS t(pedido_id, transportista);
```

Compruébalo: `python verify.py left-join-where`

## Relacionadas

- [¿Por qué NOT IN devuelve cero filas?](not-in-nulos.md)
- [¿Por qué el WHERE no encuentra a quien 'siempre' paga en efectivo?](where-vs-having.md)
- [¿Cuándo se solapan de verdad dos intervalos de tiempo?](solape-de-intervalos.md)

Página con más contexto: https://caso-abierto.christianvadillo.workers.dev/trampas/left-join-where
