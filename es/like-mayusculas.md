# ¿Por qué LIKE no encuentra un nombre que sí está en la tabla?

LIKE compara carácter por carácter y distingue mayúsculas de minúsculas. Si el dato real viene en mayúsculas, en minúsculas o sin acentos, un patrón bien escrito no encuentra filas que están justo delante.

## Cuándo aparece

Búsquedas de texto libre sobre nombres, direcciones o cualquier campo que la gente escribe a mano: mayúsculas, minúsculas y acentos nunca son consistentes entre sistemas.

## La consulta con la trampa

```sql
SELECT *
FROM huespedes
WHERE nombre LIKE '%Vela%';
-- el recepcionista dice que Vela durmió 3 noches; esto sólo encuentra 1:
-- 'VELA, ANDRES' y 'vela andres' no coinciden con '%Vela%'
```

## La corrección

```sql
SELECT *
FROM huespedes
WHERE nombre ILIKE '%vela%';
```

## Por qué

`LIKE` es sensible a mayúsculas en DuckDB (como en la mayoría de motores, salvo que la columna use una collation especial): `'VELA, ANDRES' LIKE '%Vela%'` es falso, letra por letra, no una aproximación. `ILIKE` hace la misma comparación ignorando mayúsculas y minúsculas. Queda un problema hermano que `ILIKE` no arregla: los acentos. `'andres' ILIKE '%andrés%'` también es falso, porque a la base le importa la tilde tanto como la mayúscula; para eso hace falta normalizar los dos lados con `strip_accents()` antes de comparar. Ninguno de los dos motores avisa cuando el patrón no encuentra nada: cero filas se lee como 'no hay nadie', no como 'busqué mal'.

## Dataset mínimo para reproducirla

```sql
CREATE TABLE huespedes AS SELECT * FROM (VALUES
  ('Ibarra Tomas', 102, DATE '2026-03-01'),
  ('Vela Andres', 204, DATE '2026-03-02'),
  ('Nava Lucia', 311, DATE '2026-03-05'),
  ('VELA, ANDRES', 311, DATE '2026-03-09'),
  ('vela andres', 204, DATE '2026-03-15')
) AS t(nombre, habitacion, llegada);
```

Compruébalo: `python verify.py like-mayusculas`

## Relacionadas

- [¿Por qué la transferencia más grande del mes sale como $990?](numero-como-texto.md)
- [¿Por qué NOT IN devuelve cero filas?](not-in-nulos.md)
- [¿Por qué COUNT(columna) da menos que COUNT(*)?](count-vs-asterisco.md)

Página con más contexto: https://caso-abierto.christianvadillo.workers.dev/trampas/like-mayusculas
