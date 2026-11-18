# SQL schema, data, and assignment queries

The database is MySQL-specific. Use a disposable MySQL 8 instance; query-plan
scripts use `EXPLAIN ANALYZE`, optimizer trace, index hints, and optimizer switches
whose behavior depends on the server version. MariaDB compatibility has not been
established. Configure the Python CLI through the [CLI guide](../cli/README.md).

## Installation and data

`db137 create-db` executes these files in order:

1. [install.sql](install.sql): drops and recreates `pulse_university`, then creates
   tables, keys, checks, and lookup data.
2. [indexing.sql](indexing.sql): query-oriented indexes.
3. [procedures.sql](procedures.sql): stored procedures.
4. [triggers.sql](triggers.sql): scheduling, staffing, ticketing, and resale logic.
5. [views.sql](views.sql): derived query views.

`create-db` is destructive even without `--yes`. The SQL contains literal
`pulse_university` references; retain that schema name unless deliberately
reviewing all SQL and generator references.

From the repository root with the configured virtual environment:

```bash
.venv/bin/db137 load-db
.venv/bin/db137 db-status
```

`load-db` first invokes `create-db`, then executes the committed [load.sql](load.sql).
It does not append data to an existing schema. Alternatives are mutually exclusive:

| Command | Actual behavior |
|---|---|
| `db137 load-db --i` | Run `code/data_generation/faker.py`; recreate and populate the live database |
| `db137 load-db --g` | Run `faker_sql.py` against a live database, overwrite `load.sql`, recreate the schema again, then execute that generated SQL |
| `db137 reset-db` | Drop the database, then perform the default load workflow |
| `db137 erase-db` | Truncate non-lookup tables while preserving schema |

The generators use random seed 42, different fixed reference dates, and scenario
rules for assignment-query coverage. `load.sql` is retained generated data;
constraint compliance on a new server requires an executed integration check.

## Queries and retained results

[queries/](queries/) contains `Q01.sql` through `Q15.sql`, their recorded outputs,
and alternative-plan outputs for Q04 and Q06.

```bash
.venv/bin/db137 q 8
.venv/bin/db137 q 1 6
```

The CLI writes directly to `sql/queries/Qxx_out.txt`. For Q04 and Q06 it writes
`Qxx_plan1_out.txt`, `Qxx_plan2_out.txt`, and `Qxx_plan3_out.txt`. Copy the repository
to a disposable working location or preserve these files before a new run;
execution can overwrite historical evidence. Plan output and timings describe
the original server/data, not a portable performance guarantee.

The [report](../docs/report.pdf), [DDL reference](../docs/ddl.pdf), and
[diagrams](../diagrams/README.md) document the original design and analysis.
