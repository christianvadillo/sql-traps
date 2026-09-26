# ¿Por qué NOT IN devuelve cero filas?

NOT IN contra una lista con un solo NULL descarta la consulta entera sin avisar. Es el peor fallo posible: no revienta, da tranquilidad.

## Cuándo aparece

Cualquier antijoin (buscar lo que falta, lo que no coincide, lo que no se registró) escrito con NOT IN sobre una columna que admite NULL. Es una pregunta clásica de entrevista de SQL porque parece inofensiva.

## La consulta con la trampa

```sql
SELECT nombre
FROM personas
WHERE nombre NOT IN (
  SELECT nombre FROM coartadas
);
-- coartadas tiene una fila con nombre NULL (un recibo sin firma):
-- la consulta entera devuelve cero filas, aunque haya sospechosos sin coartada
```

## La corrección

```sql
SELECT nombre
FROM personas p
WHERE NOT EXISTS (
  SELECT 1 FROM coartadas c WHERE c.nombre = p.nombre
);
-- o, filtrando el NULL dentro de la propia lista:
WHERE nombre NOT IN (
  SELECT nombre FROM coartadas WHERE nombre IS NOT NULL
)
```

## Otra forma de corregirla

```sql
SELECT nombre
FROM personas
WHERE nombre NOT IN (
  SELECT nombre FROM coartadas WHERE nombre IS NOT NULL
);
```

## Por qué

`x NOT IN (a, b, NULL)` no es una lista con un hueco: es `x<>a AND x<>b AND x<>NULL`, y esa última comparación da `NULL`, no verdadero ni falso. Una conjunción con un `NULL` nunca da verdadero, así que ninguna fila pasa el filtro, sin importar cuántos nombres falten de verdad. `NOT EXISTS` no compara con la lista entera: pregunta fila por fila, y un `NULL` en la subconsulta no contamina a las demás. La otra salida es quitar el `NULL` antes de que llegue al `NOT IN`, pero eso obliga a acordarse cada vez; `NOT EXISTS` es la opción segura por defecto.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE personas AS SELECT * FROM (VALUES ('Ruiz'), ('Salas'), ('Ortega'), ('Bravo'), ('Mendez')) AS t(nombre);
CREATE TABLE coartadas AS SELECT * FROM (VALUES ('Ruiz', 'camara del bar'), ('Salas', 'su hermana'), (NULL, 'recibo sin firma'), ('Bravo', 'turno de noche')) AS t(nombre, confirma);
```

Compruébalo: `python verify.py not-in-nulos`

## Relacionadas

- [Un WHERE sobre la tabla derecha convierte tu LEFT JOIN en INNER](left-join-where.md)
- [¿Por qué COUNT(columna) da menos que COUNT(*)?](count-vs-asterisco.md)
- [¿Por qué el WHERE no encuentra a quien 'siempre' paga en efectivo?](where-vs-having.md)

Página con más contexto: https://casoabiertogame.com/trampas/not-in-nulos
