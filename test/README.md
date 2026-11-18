# Pulse University validation

## Current bounded frontend check

On 18 November 2026, seven tests passed on Node v24.20.0 in a disposable
copy of `frontend/`, with zero failures or skips.

```bash
node --test test/client.test.mjs test/logout.test.mjs
```

The tests use request doubles for authenticated client behavior and logout
races. Live browser login and database workflows remain outside this verification. [Frontend guide](../frontend/README.md)

## Web-session tests

All eight Python session tests passed on Python 3.12.14 using the Flask
test client in a disposable environment. It covers opaque tokens, authorization, revocation,
expiry, capacity, and serialized CLI calls with the MySQL boundary
blocked. The web extra and a configured private virtual environment are
prerequisites. Run the suite from the repository root:

```bash
.venv/bin/python -m unittest discover -s test -p 'test_web_sessions.py' -v
```

The check used Flask 3.1.3, flask-cors 6.0.5 and MySQL Connector/Python
9.7.0. The test client runs in-process with MySQL calls mocked.

## Historical CLI evidence

The redacted [historical CLI transcript](test_cli_results.txt) records
24 passed and zero failed checks. The
[historical shell runner](test_cli.sh) changes the database and writes its
transcript. It creates, grants, renames, and drops accounts. Inspection of
the recorded results is independent of running the script. If replay is
needed, use a disposable project copy and isolated MySQL instance with
synthetic data and preserve the original transcript and query outputs.
[Redaction record](REDACTION.md)
