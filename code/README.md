# Data generation and repository utilities

These scripts support Team 137's database submission. Install the `data` extra
and configure a disposable MySQL instance using the [CLI guide](../cli/README.md).
Data generation is a live, destructive database operation.

## Generators

| Script | Behavior and output |
|---|---|
| [data_generation/faker.py](data_generation/faker.py) | Calls `create-db`, inserts synthetic festival data, writes `docs/organization/db_data.txt` |
| [data_generation/faker_sql.py](data_generation/faker_sql.py) | Calls `create-db`, executes generated statements against MySQL, writes successful statements to `sql/load.sql`, and writes the row-count summary |

Both scripts seed Python's random generator with 42. Their fixed `TODAY` values
differ (`2025-05-13` and `2025-05-08` respectively); they are related coursework
generators, not interchangeable byte-identical exports. They target the schema/triggers and assignment scenarios. Run them through `db137 load-db --i` or
`db137 load-db --g` as described in the [SQL guide](../sql/README.md).

## Maintenance scripts

- [code_utils/dropgen.py](code_utils/dropgen.py) rewrites generated DROP blocks in
  SQL definition files.
- [code_utils/fixeof.py](code_utils/fixeof.py) normalizes file endings.
- [code_utils/qgen.py](code_utils/qgen.py) creates absent or empty query/output
  placeholders.
- [organization/struct.py](organization/struct.py) generates repository structure
  notes.
- [runall.py](runall.py) runs `code_utils/`, then `organization/`. Its current
  implementation does **not** run `data_generation/`.

These are source-maintenance tools, not required application startup steps.
Review their target paths and work in a disposable copy before running them:
SQL sources, recorded query outputs, and organization notes are part of the
retained submission.
