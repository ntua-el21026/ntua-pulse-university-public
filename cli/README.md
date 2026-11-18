# Pulse University – DB137 CLI

The Team 137 CLI administers a local MySQL festival database and executes the
course queries. It can create/drop schemas, manage accounts and privileges, and
load synthetic data. Use a disposable database that you own.

## Installation

Use Python 3.10+ and a private virtual environment from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[web,data]'
.venv/bin/db137 --help
```

`pyproject.toml` defines the CLI entry point and optional web/data dependencies;
do not create an ad-hoc manifest. Dependency ranges are declared, but no exact
Python lock is supplied. A fresh editable installation and `db137 --help` were
checked with Python 3.14 in November 2026; this does not validate MySQL behavior.
No system Python or global package installation is required.

## Database configuration

Set `DB_HOST` (default `localhost`), `DB_PORT` (default `3306`), and `DB_NAME`
(default `pulse_university`). `DB_ROOT_USER` and `DB_ROOT_PASS` are required
by the CLI. These names are historical: use the least-privileged database
account suitable for the selected operation. Schema/user administration needs
additional grants; arbitrary SQL remains subject to MySQL permissions.

In a private local shell, read the password without putting it in command history:

```bash
export DB_HOST=127.0.0.1 DB_PORT=3306 DB_NAME=pulse_university
read -r -p 'Local database user: ' DB_ROOT_USER
read -r -s -p 'Local database password: ' DB_ROOT_PASS
export DB_ROOT_USER DB_ROOT_PASS
.venv/bin/db137 db-status
```

Do not echo credentials, commit `.envrc`, or use production grants. Schema reset,
user dropping, and data loading commands mutate or delete data. Review each
command before execution. `test/test_cli.sh` is a historical mutating integration
runner, documented in [the test guide](../test/README.md).

## Command reference

Each of the following commands can be run with:

```bash
db137 <command>
```

---

### USERS

- `users register` – Create a new user and grant privileges:

  **Required**:
  - `username` (e.g. `alice`)
  - `--password` (e.g. `--password secret`)

  **Optional**:
  - `--default-db` (default: `pulse_university`)
  - `--privileges` (default: `FULL`)

  Example:
  ```bash
  db137 users register alice --password secret --default-db pulse_university --privileges SELECT,INSERT
  ```

- `users grant` – Grant privileges on a schema:

  **Required**:
  - `username` (e.g. `alice`)
  - `--db` (e.g. `--db pulse_university`)
  - `--privileges` (e.g. `--privileges SELECT,INSERT`)

  **Optional**:
  - `--show-diff` (shows before/after privileges)

  Example:
  ```bash
  db137 users grant alice --db pulse_university --privileges SELECT,INSERT --show-diff
  ```

- `users revoke` – Revoke privileges from a user:

  **Required**:
  - `username` (e.g. `alice`)
  - `--db` (e.g. `--db pulse_university`)
  - `--privileges` (e.g. `--privileges SELECT`)

  **Optional**:
  - `--show-diff` (shows before/after privileges)

  Example:
  ```bash
  db137 users revoke alice --db pulse_university --privileges SELECT --show-diff
  ```

- `users rename` – Rename a user:
  ```bash
  db137 users rename alice alicia
  ```

- `users passwd` – Change a user's password:
  ```bash
  db137 users passwd alice
  ```

- `users list` – List users and their privileges:
  ```bash
  db137 users list
  ```

- `users drop` – Drop a user:
  ```bash
  db137 users drop alice
  ```

- `users drop-all` – Drop all users on host `%`:
  ```bash
  db137 users drop-all
  ```

- `users whoami` – Show current connection identity:
  ```bash
  db137 users whoami
  ```

- `users set-defaults` – Grant standard CRUD privileges:

  **Required**:
  - `username` (e.g. `alice`)

  **Optional**:
  - `--db` (default: `pulse_university`)
  - `--show-diff` (shows before/after privileges)

  Example:
  ```bash
  db137 users set-defaults alice --show-diff
  ```

---

### DATABASE SETUP

`create-db` and every `load-db` mode recreate the schema. `install.sql` contains
`DROP DATABASE` and a literal `pulse_university` name. Keep that name for the
supplied workflow; `--database` alone does not rename the SQL schema. Query
commands overwrite retained output files. See [the SQL guide](../sql/README.md).

- `create-db` – Deploy schema, indexing, views, and triggers:

  **Optional**:
  - `--sql-dir` (default: `sql`)
  - `--database` (default: `pulse_university`)

  Example:
  ```bash
  db137 create-db --sql-dir sql --database pulse_university
  ```

- `drop-db` – Delete the database schema:

  **Optional**:
  - `--database` (default: `pulse_university`)
  - `--yes` (skip confirmation prompt)

  Example:
  ```bash
  db137 drop-db --database pulse_university --yes
  ```

- `reset-db` – Full setup (drop + create + load):

  **No arguments required or optional.**

  Example:
  ```bash
  db137 reset-db
  ```

- `load-db` – Load synthetic data into the database, either from SQL or Python generators.

  **Behavior**:
  - By default, recreates the schema via `create-db`, then loads data from `load.sql`
  - `--g` → Run `faker_sql.py` (basic generator), then execute `create-db` and `load.sql` with progress bar
  - `--i` → Run `faker.py` (intelligent, trigger-compliant generator)

  **Optional**:
  - `--g` (run `faker_sql.py` + `load.sql`)
  - `--i` (run only `faker.py`)
  - `--sql-dir` (directory containing SQL files; default: `sql`)
  - `--database` (database to load into; default: `pulse_university`)

  `--g` and `--i` are mutually exclusive.

  **Example**:
  ```bash
  db137 load-db
  db137 load-db --g
  db137 load-db --i
  ```

- `erase-db` – Truncate non-lookup tables while retaining the schema and lookup tables:

  **Optional**:
  - `--database` (default: `pulse_university`)
  - `--yes` (skip confirmation prompt)

  Example:
  ```bash
  db137 erase-db --database pulse_university --yes
  ```

- `db-status` – Print row counts for all base tables:

  **Optional**:
  - `--database` (default: `pulse_university`)

  Example:
  ```bash
  db137 db-status --database pulse_university
  ```

- `viewq` – Show contents of the Resale_Match_Log table:

  **Optional**:
  - `--database` (default: `pulse_university`)

  Example:
  ```bash
  db137 viewq --database pulse_university
  ```

---

### QUERIES

- `q X` – Run one query (e.g., `Q01.sql → Q01_out.txt`):

  **Required**:
  - `q X` (query number, e.g. `q 1`, `q 14`)

  **Optional**:
  - `--database` (default: `pulse_university`)

  Example:
  ```bash
  db137 q 1 --database pulse_university
  ```

- `q X Y` – Run a query batch:

  **Required**:
  - `q X Y` (range format, e.g. `q 1 5`)

  **Optional**:
  - `--database` (default: `pulse_university`)

  Example:
  ```bash
  db137 q 1 5 --database pulse_university
  ```
