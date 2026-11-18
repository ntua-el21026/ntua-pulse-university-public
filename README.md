# Pulse University Festival Database

Pulse University is Team 137’s relational database project for the Spring 2025 Databases course at NTUA ECE. It demonstrates database design for festival scheduling, staff assignments, ticket sales and resale, and attendee reviews. The project combines a MySQL schema and workload with a Python administration CLI and a React/Flask interface.

## Engineering contribution

- The [SQL implementation](sql/README.md) combines primary and foreign keys, table-level checks, and triggers for cross-record rules such as stage overlap, event date boundaries, and ticket capacity. Stored procedures support scheduling, staffing, ticketing, and resale workflows.
- The [query workload](sql/queries/) contains 15 queries with retained outputs. For Q04 and Q06, the team examined alternative access and join strategies using MySQL plan output, optimizer settings, and index hints. The [report](docs/report.pdf) explains the interpretation of those recorded plans.
- The [data generators](code/README.md) create synthetic festival records. The [DB137 CLI](cli/README.md) manages the schema and queries. The [web demonstration](frontend/README.md) presents schema browsing, SQL execution, and CLI administration through a local Flask API.

## Evidence and limitations

The [design diagrams](diagrams/README.md), [DDL reference](docs/ddl.pdf), [report](docs/report.pdf), and [documentation guide](docs/README.md) retain the team’s design and analysis. The project description is attributed to the NTUA course and linked through the guide. The report retains its technical pages and two regenerated authentication-screen captures. The guide identifies the relationship between the current PDF and the LaTeX source, including figures needed for a complete rebuild.

On 18 November 2026, seven offline frontend tests passed on Node v24.20.0 in a disposable copy. They exercise request handling and logout races using request doubles. Eight additional Python 3.12 web-session tests passed with the in-process Flask client and a mocked MySQL boundary. The historical CLI transcript records 24 passing checks. Live MySQL and end-to-end browser behavior remain unverified. Recorded query-plan results reflect the original data, server, and optimizer configuration. [Test scope and commands](test/README.md)

## Local reproduction

Use Python 3.10+, Node/npm, and MySQL 8 with `EXPLAIN ANALYZE` and the optimizer settings used by the supplied queries. The [Python manifest](pyproject.toml) declares the package and optional web/data dependencies. The frontend has an npm lockfile. The Python/server environment is version-bounded by the package and setup guides, with no exact Python dependency lock or bundled server image.

Follow the [CLI setup](cli/README.md) to create a virtual environment and configure the database connection. The SQL uses the literal schema name `pulse_university`. Use a disposable local MySQL instance and a separate copy of the repository for reruns.

```bash
.venv/bin/db137 --help
# Recreates the schema and loads the committed synthetic data.
.venv/bin/db137 load-db
.venv/bin/db137 db-status
# Executes a query and rewrites its corresponding stored output in this copy.
.venv/bin/db137 q 8
```

The [SQL guide](sql/README.md) identifies the installation order, generator behavior and output paths. The [web guide](frontend/README.md) describes the separate loopback Vite and Flask processes, including their session and database-grant assumptions.

## Team and licensing

The [report source](docs/main.tex) credits Team 137 as **Michail Athanasios Peppas**, **Andreas Tsouvalas**, and **Konstantinos Mantzaris**. The schema, queries, utilities, web demonstration, diagrams, and report are shared coursework. The [MIT notice](LICENSE) applies to original contributions within its scope. The NTUA assignment and third-party materials have their own terms. The authentication screens use a project-specific database emblem.
