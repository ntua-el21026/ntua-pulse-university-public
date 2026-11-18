# Pulse University web administration demo

React/Vite presents schema browsing, SQL execution, and the DB137 CLI through a
local Flask API. MySQL grants enforce database operations. This is a local,
single-process administrative demonstration, not a public user portal.

## Setup

From the repository root, install the Python package as described in
[the CLI guide](../cli/README.md), including the `web` extra. Then:

```bash
cd frontend
npm ci
npm run build
npm run dev -- --host 127.0.0.1
```

In a second terminal at the repository root:

```bash
.venv/bin/python frontend/src/api/serve.py
```

Use `http://localhost:3000`; Flask binds `127.0.0.1:8000` with debugging disabled.
The allowed browser origins are `http://localhost:3000` and
`http://127.0.0.1:3000`. Match `DB_HOST`, `DB_PORT`, and `DB_NAME` to the local
instance. Frontend dependencies are recorded in `package-lock.json`; Python
ranges are in the root manifest. Installation does not configure MySQL.

## Sessions and permissions

Login sends a database username/password once to the local API. A random opaque
bearer token is returned; the password remains in server process memory for a
15-minute session and is never included in the browser token. Requests resolve the
token server-side. Logout clears the browser immediately and requests revocation using the captured
old token. Delayed/failing requests never erase a newer login. Server revocation
needs a reachable API; otherwise the old token remains valid until expiry.
Expiry is enforced by the server, and a
restart invalidates all sessions. The store is bounded to 128 active sessions; expired credential records are
pruned on subsequent login/authentication, or cleared at process exit.
The supported Flask launch is single-process with `threaded=False`. CLI invocations
also hold a process-local lock because Click's runner temporarily replaces global
environment/standard streams. This serializes CLI requests even in a threaded
single-process embedding; it is not multi-worker support or a background job
system. The browser keeps the opaque token in sessionStorage; the demo has no persistent
session store, TLS termination, multi-worker support, or production protection
against browser compromise. Use a synthetic database with restricted accounts.

SQL/CLI execution is intentional administration functionality. Hiding a command
in the UI does not grant or revoke MySQL permissions. Schema definition endpoints
also require a valid session. Do not expose Flask/Vite through a public tunnel.

## Presentation captures

The `/logo.jpg` asset is the project-specific database emblem.
The login and logout captures were rendered offline from the existing
screen layouts with that emblem and fictional details. The
[report and asset guide](../docs/README.md) explains the original photograph,
its replacement, and the current PDF. The other four
[interface captures](public/frontend_images/) remain historical evidence.

## Offline tests

The [test evidence](../test/README.md) distinguishes the seven current
Node tests, earlier Python session results, and the historical CLI run.
Run the Node tests from this directory with `npm test`. They exercise
authenticated API client behavior and delayed or failed logout requests
using doubles. The project’s Python session test requires the web extra
in the private virtual environment.
