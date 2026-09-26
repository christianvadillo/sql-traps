# SQL traps

Fifteen SQL mistakes that don't throw an error. The query runs, returns something that looks reasonable, and it's wrong.

Each one comes with the query that has the trap, the fix, why it happens, and a minimal dataset. `verify.py` runs all of them in DuckDB and checks that the broken query and the fixed one really give different results, in the way the page says. Nothing here is just asserted.

In English and in Spanish.

| Trap |
|---|
| [The join that multiplies rows](en/fanout.md) |
| [A rate needs a denominator](en/tasa-sin-denominador.md) |
| [A WHERE on the right-hand table turns your LEFT JOIN back into an INNER JOIN](en/left-join-where.md) |
| [Survivorship bias lives in the JOIN](en/supervivencia.md) |
| [Time zones: store UTC, show local](en/husos-horarios.md) |
| [Why does NOT IN return zero rows?](en/not-in-nulos.md) |
| [Why does COUNT(column) give a smaller number than COUNT(*)?](en/count-vs-asterisco.md) |
| [Why doesn't LIKE find a name that's right there in the table?](en/like-mayusculas.md) |
| [Why does the biggest transfer of the month show up as $990?](en/numero-como-texto.md) |
| [Why does BETWEEN eat the last day of the range?](en/between-medianoche.md) |
| [Why does a self-join always bring back one extra row?](en/self-join-trivial.md) |
| [When do two time intervals actually overlap?](en/solape-de-intervalos.md) |
| [Why does the running balance repeat the exact same number on two different rows?](en/rango-vs-filas.md) |
| [Why can't WHERE filter on a window function's result?](en/qualify-vs-where.md) |
| [Why doesn't WHERE find the customer who 'always' pays cash?](en/where-vs-having.md) |

## Run the checks

```bash
pip install duckdb
python verify.py            # all of them
python verify.py fanout     # just one
```

The SQL is DuckDB. Almost all of it is plain standard SQL; where an engine behaves differently (for example, DuckDB's `/` never does integer division) the page says so.

## Where these come from

They are the traps hidden in the case files of [Caso Abierto](https://casoabiertogame.com/?via=github-traps), a detective game where you solve each case by writing SQL and have to hand in the query that proves your accusation. The first case plays free in the browser.

---

# Trampas de SQL

Quince errores de SQL que no dan error. La consulta corre, devuelve algo razonable y está mal.

Cada una trae la consulta con la trampa, la corrección, por qué pasa y un dataset mínimo. `verify.py` las ejecuta todas en DuckDB y comprueba que la consulta rota y la corregida dan resultados distintos, en el sentido que explica cada página.

| Trampa |
|---|
| [El join que multiplica filas](es/fanout.md) |
| [Una tasa sin denominador no significa nada](es/tasa-sin-denominador.md) |
| [Un WHERE sobre la tabla derecha convierte tu LEFT JOIN en INNER](es/left-join-where.md) |
| [El sesgo de supervivencia está en el JOIN](es/supervivencia.md) |
| [Zonas horarias: guarda UTC, muestra local](es/husos-horarios.md) |
| [¿Por qué NOT IN devuelve cero filas?](es/not-in-nulos.md) |
| [¿Por qué COUNT(columna) da menos que COUNT(*)?](es/count-vs-asterisco.md) |
| [¿Por qué LIKE no encuentra un nombre que sí está en la tabla?](es/like-mayusculas.md) |
| [¿Por qué la transferencia más grande del mes sale como $990?](es/numero-como-texto.md) |
| [¿Por qué BETWEEN se come el último día del rango?](es/between-medianoche.md) |
| [¿Por qué un self-join siempre trae una fila de más?](es/self-join-trivial.md) |
| [¿Cuándo se solapan de verdad dos intervalos de tiempo?](es/solape-de-intervalos.md) |
| [¿Por qué el saldo acumulado repite el mismo número en dos filas distintas?](es/rango-vs-filas.md) |
| [¿Por qué WHERE no puede filtrar el resultado de una window function?](es/qualify-vs-where.md) |
| [¿Por qué el WHERE no encuentra a quien 'siempre' paga en efectivo?](es/where-vs-having.md) |

Salen de los casos de [Caso Abierto](https://casoabiertogame.com/?via=github-trampas), un juego de detectives que se resuelve escribiendo SQL. El primer caso se juega gratis en el navegador.

## License

Text: CC BY 4.0. Code (`verify.py`): MIT.
