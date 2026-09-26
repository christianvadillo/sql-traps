# ¿Por qué el saldo acumulado repite el mismo número en dos filas distintas?

sum(...) OVER (ORDER BY fecha) sin especificar el marco usa RANGE por defecto: agrupa todas las filas con la misma fecha en un único bloque, y todas enseñan el mismo acumulado.

## Cuándo aparece

Cualquier saldo corrido, total acumulado o ranking calculado con una window function cuando el ORDER BY tiene valores empatados (dos movimientos el mismo día, dos ventas a la misma hora).

## La consulta con la trampa

```sql
SELECT fecha, importe,
       sum(importe) OVER (ORDER BY fecha) AS saldo
FROM movimientos;
-- dos apuntes del mismo día caen en el mismo RANGE:
-- ambos enseñan el saldo ya sumando los dos, ninguno el saldo intermedio
```

## La corrección

```sql
SELECT fecha, importe,
       sum(importe) OVER (
         ORDER BY fecha
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS saldo
FROM movimientos;
```

## Por qué

Cuando hay `ORDER BY` en una window function pero no se especifica el marco, el motor asume `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, y `RANGE` agrupa por *valor*, no por fila: todas las filas con el mismo valor de `ORDER BY` quedan en el mismo punto del marco, así que todas ven la misma suma, la de después de sumarlas todas. `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` avanza fila por fila sin que le importen los empates: la primera de las dos filas del mismo día ve el saldo antes de sumar la segunda, y la segunda ve el saldo con las dos. La regla práctica: si la palabra es 'saldo corrido' o 'acumulado hasta esta fila', casi siempre quieres `ROWS`, no el `RANGE` que se aplica sin pedirlo.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE movimientos AS SELECT * FROM (VALUES
  (DATE '2026-04-01', 100.0),
  (DATE '2026-04-02', 50.0),
  (DATE '2026-04-02', 30.0),
  (DATE '2026-04-03', 20.0)
) AS t(fecha, importe);
```

Compruébalo: `python verify.py rango-vs-filas`

## Relacionadas

- [¿Por qué WHERE no puede filtrar el resultado de una window function?](qualify-vs-where.md)
- [Zonas horarias: guarda UTC, muestra local](husos-horarios.md)
- [¿Por qué la transferencia más grande del mes sale como $990?](numero-como-texto.md)

Página con más contexto: https://casoabiertogame.com/trampas/rango-vs-filas
