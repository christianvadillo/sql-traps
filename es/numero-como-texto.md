# ¿Por qué la transferencia más grande del mes sale como $990?

Si el monto se guardó como texto, ORDER BY lo compara letra por letra: '9' va antes que '75000' porque el primer carácter de '990' es más grande, sin que importen las cifras que vienen después.

## Cuándo aparece

Columnas numéricas importadas de un CSV, una API o un formulario, que llegaron como VARCHAR y nadie las convirtió. Ordenarlas o compararlas tal cual da un orden que parece aleatorio.

## La consulta con la trampa

```sql
SELECT cuenta, monto
FROM transferencias
ORDER BY monto DESC
LIMIT 3;
-- monto es VARCHAR: '990' > '9500' > '870' porque se compara
-- carácter a carácter, y la de 75,000 pesos no aparece
```

## La corrección

```sql
SELECT cuenta, monto
FROM transferencias
ORDER BY CAST(monto AS BIGINT) DESC
LIMIT 3;
-- TRY_CAST en vez de CAST si alguna fila puede traer texto no numérico
-- (una coma de miles, una celda vacía): TRY_CAST da NULL en vez de reventar la consulta
```

## Por qué

Un `VARCHAR` se ordena como texto: compara el primer carácter, y sólo si empatan mira el segundo. `'990'` gana a `'75000'` porque `'9' > '7'`, sin que a la comparación le importe que a `'75000'` le sobren cifras. `CAST(monto AS BIGINT)` convierte antes de ordenar, y ahí `75000` sí es mayor que `990`. La diferencia entre `CAST` y `TRY_CAST` importa en datos reales: `CAST` revienta la consulta entera si una sola fila trae `'12,000'` con coma o una celda vacía; `TRY_CAST` convierte esa fila en `NULL` y deja que las demás sigan. Cuál de los dos usar depende de si quieres enterarte del dato sucio ahora o más tarde.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE transferencias AS SELECT * FROM (VALUES
  ('MX-1041', '1500'), ('MX-2208', '9500'), ('MX-0317', '75000'),
  ('MX-1190', '870'), ('MX-4402', '12000'), ('MX-3315', '8200'), ('MX-0928', '990')
) AS t(cuenta, monto);
```

Compruébalo: `python verify.py numero-como-texto`

## Relacionadas

- [¿Por qué LIKE no encuentra un nombre que sí está en la tabla?](like-mayusculas.md)
- [¿Por qué el WHERE no encuentra a quien 'siempre' paga en efectivo?](where-vs-having.md)
- [¿Por qué el saldo acumulado repite el mismo número en dos filas distintas?](rango-vs-filas.md)

Página con más contexto: https://casoabiertogame.com/trampas/numero-como-texto
