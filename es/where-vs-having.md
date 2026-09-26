# ¿Por qué el WHERE no encuentra a quien 'siempre' paga en efectivo?

Filtrar en el WHERE antes de agrupar responde otra pregunta: cuenta a quien pagó en efectivo varias veces, no comprueba que pagara SIEMPRE así. 'Siempre' describe el grupo entero, y eso se comprueba en el HAVING.

## Cuándo aparece

Cualquier pregunta con 'siempre', 'nunca' o 'todas las veces': hay que dejar que el grupo entero llegue al GROUP BY antes de decidir si cumple la regla.

## La consulta con la trampa

```sql
SELECT cliente
FROM pagos
WHERE metodo = 'efectivo'
GROUP BY cliente
HAVING count(*) >= 3;
-- esto encuentra a quien pagó en efectivo 3 veces o más,
-- aunque también haya pagado con tarjeta: el WHERE ya borró esa fila
```

## La corrección

```sql
SELECT cliente
FROM pagos
GROUP BY cliente
HAVING count(*) >= 3
   AND count(*) FILTER (WHERE metodo <> 'efectivo') = 0;
```

## Por qué

El `WHERE metodo = 'efectivo'` corre antes del `GROUP BY`: borra las filas con tarjeta ANTES de que el grupo se forme, así que el `HAVING count(*) >= 3` sólo ve las filas de efectivo que sobrevivieron y nunca se entera de que ese cliente también pagó con tarjeta alguna vez. Lo que responde de verdad esa consulta es '¿pagó en efectivo al menos tres veces?', no '¿pagó siempre en efectivo?'. Para preguntar por el grupo completo hay que dejar que el grupo completo llegue al `GROUP BY`: quitar el `WHERE` y usar `count(*) FILTER (WHERE metodo <> 'efectivo') = 0` para exigir que ninguna fila incumpla, junto con `count(*) >= 3` para pedir un mínimo de datos. `FILTER` cuenta condicionalmente sin necesidad de borrar filas antes de que el grupo se complete.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE pagos AS SELECT * FROM (VALUES
  ('X', 'efectivo'), ('X', 'efectivo'), ('X', 'efectivo'),
  ('Y', 'efectivo'), ('Y', 'efectivo'), ('Y', 'efectivo'), ('Y', 'tarjeta'),
  ('Z', 'efectivo'), ('Z', 'efectivo')
) AS t(cliente, metodo);
```

Compruébalo: `python verify.py where-vs-having`

## Relacionadas

- [Una tasa sin denominador no significa nada](tasa-sin-denominador.md)
- [¿Por qué COUNT(columna) da menos que COUNT(*)?](count-vs-asterisco.md)
- [¿Por qué NOT IN devuelve cero filas?](not-in-nulos.md)

Página con más contexto: https://casoabiertogame.com/trampas/where-vs-having
