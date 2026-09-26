# ¿Por qué un self-join siempre trae una fila de más?

Unir una tabla contra sí misma sin excluir la fila consigo misma hace que cada registro se empareje con su propia copia: una fila que no dice nada, pero que sí cuenta.

## Cuándo aparece

Comparar filas de la misma tabla entre sí: quién coincidió con quién, duplicados, pares, solapes. Cualquier self-join sin una condición que descarte la pareja trivial.

## La consulta con la trampa

```sql
SELECT o.socio, o.desde, v.socio AS con_quien
FROM estancias o
JOIN estancias v
  ON o.sala = v.sala
 AND o.desde < v.hasta
 AND v.desde < o.hasta;
-- cada estancia solapa consigo misma (o.socio = v.socio en dos filas):
-- esas filas no aportan nada y encima inflan cualquier conteo posterior
```

## La corrección

```sql
SELECT o.socio, o.desde, v.socio AS con_quien
FROM estancias o
JOIN estancias v
  ON o.sala = v.sala
 AND o.id <> v.id
 AND o.desde < v.hasta
 AND v.desde < o.hasta;
```

## Por qué

Sin una condición que compare la clave de una copia contra la otra, cada fila de la tabla siempre encuentra pareja consigo misma: mismo salón, mismo horario, solapa perfectamente porque es la misma estancia. `o.id <> v.id` (o el equivalente con la clave primaria) elimina exactamente esas filas y sólo esas. El error es fácil de no ver porque la fila trivial suele parecer razonable a simple vista, alguien 'coincidió consigo mismo', y sólo se nota cuando el resultado trae más filas de las esperadas, o cuando un `count(*)` posterior sale inflado en exactamente una unidad por cada fila original.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE estancias AS SELECT * FROM (VALUES
  (1, 'A', 'Reservado 3', TIMESTAMP '2026-06-02 23:10', TIMESTAMP '2026-06-02 23:55'),
  (2, 'B', 'Reservado 3', TIMESTAMP '2026-06-02 23:25', TIMESTAMP '2026-06-02 23:50')
) AS t(id, socio, sala, desde, hasta);
```

Compruébalo: `python verify.py self-join-trivial`

## Relacionadas

- [¿Cuándo se solapan de verdad dos intervalos de tiempo?](solape-de-intervalos.md)
- [El join que multiplica filas](fanout.md)
- [El sesgo de supervivencia está en el JOIN](supervivencia.md)

Página con más contexto: https://caso-abierto.christianvadillo.workers.dev/trampas/self-join-trivial
