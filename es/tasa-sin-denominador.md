# Una tasa sin denominador no significa nada

Un conteo por sí solo premia a quien más aparece; una tasa sin un mínimo de muestra premia a quien menos aparece. Hacen falta las dos cosas.

## Cuándo aparece

Cualquier ranking de «el mejor», «el más sospechoso» o «la peor tienda»: si el resultado es una proporción, la pregunta inmediata es sobre qué se está dividiendo.

## La consulta con la trampa

```sql
SELECT tienda, count(*) AS reembolsos
FROM reembolsos
GROUP BY tienda
ORDER BY reembolsos DESC;
-- la tienda con más ventas parece la peor, aunque reembolse menos que nadie
```

## La corrección

```sql
SELECT p.tienda,
       count(r.pedido_id) * 1.0 / count(p.pedido_id) AS tasa_reembolso,
       count(p.pedido_id) AS pedidos
FROM pedidos p
LEFT JOIN reembolsos r ON r.pedido_id = p.pedido_id
GROUP BY p.tienda
HAVING count(p.pedido_id) >= 30   -- sin esto, una tienda con 2 pedidos y 1
                                   -- reembolso «gana» con 50%
ORDER BY tasa_reembolso DESC;
```

## Por qué

El conteo señala a quien más vende; la tasa sin mínimo, a quien menos, porque con pocos pedidos cualquier proporción extrema es fácil de alcanzar. Un `HAVING count(*) >= N` descarta las muestras demasiado pequeñas para que la tasa signifique algo, y conviene comparar siempre contra la tasa global: si en total se reembolsa el 5 %, 12 de 80 (15 %) llama la atención; 1 de 2 no dice nada aunque sea «el 50 %».

## Dataset mínimo para reproducirla

```sql
CREATE TABLE pedidos AS
  SELECT i AS pedido_id, 'A' AS tienda FROM range(1, 41) t(i)
  UNION ALL
  SELECT i, 'B' FROM range(101, 103) t(i);
CREATE TABLE reembolsos AS SELECT * FROM (VALUES
  (1, 'A'), (2, 'A'), (3, 'A'), (4, 'A'), (101, 'B')
) AS t(pedido_id, tienda);
```

Compruébalo: `python verify.py tasa-sin-denominador`

## Relacionadas

- [¿Por qué el WHERE no encuentra a quien 'siempre' paga en efectivo?](where-vs-having.md)
- [El join que multiplica filas](fanout.md)
- [¿Cuándo se solapan de verdad dos intervalos de tiempo?](solape-de-intervalos.md)

Página con más contexto: https://casoabiertogame.com/trampas/tasa-sin-denominador
