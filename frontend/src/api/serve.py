from flask import Flask, request, jsonify, Response, g
from http import HTTPStatus
import re
from flask_cors import CORS
import mysql.connector
import os
import sys
from pathlib import Path
import subprocess
from click.testing import CliRunner
import click
import secrets
import time
from threading import Lock

# CLI path for db137 import
cli_path = Path(__file__).resolve().parents[3] / "cli"
sys.path.insert(0, str(cli_path.parent))
sys.path.append(str(cli_path))

from users.manager import UserManager
from table_defs import get_create_statement
from sql_parser import get_definition
from cli.db137 import cli

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

from cli_list import cli_bp
app.register_blueprint(cli_bp)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DEFAULT_DB = os.getenv("DB_NAME", "pulse_university")

# Single-process local demo sessions. Credentials never leave server memory after
# login. Restarting the process invalidates every token; do not use multiple workers.
SESSION_TTL_SECONDS = 15 * 60
MAX_SESSIONS = 128
_sessions = {}
_session_lock = Lock()
# CliRunner temporarily replaces process-global environment and standard streams.
_cli_execution_lock = Lock()


def _prune_sessions(now):
    expired = [token for token, record in _sessions.items() if record[2] <= now]
    for token in expired:
        del _sessions[token]


@app.before_request
def authenticate_session():
    if not request.path.startswith("/api/") or request.path == "/api/login" or request.method == "OPTIONS":
        return None
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme != "Bearer" or not token:
        return jsonify({"error": "A login session is required"}), 401
    with _session_lock:
        _prune_sessions(time.monotonic())
        record = _sessions.get(token)
    if record is None:
        return jsonify({"error": "Session expired or invalid"}), 401
    g.database_credentials = record[:2]
    g.session_token = token


@app.after_request
def private_responses(response):
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Username and password are required"}), 400
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    try:
        um = UserManager(root_user=username, root_pass=password, host=DB_HOST, port=DB_PORT)
        um.whoami()
    except mysql.connector.Error:
        return jsonify({"error": "Invalid credentials or unavailable database"}), 401
    now = time.monotonic()
    with _session_lock:
        _prune_sessions(now)
        if len(_sessions) >= MAX_SESSIONS:
            return jsonify({"error": "Session capacity reached; retry later"}), 503
        token = secrets.token_urlsafe(32)
        _sessions[token] = (username, password, now + SESSION_TTL_SECONDS)
    return jsonify({"token": token, "expires_in": SESSION_TTL_SECONDS})


@app.route("/api/logout", methods=["POST"])
def logout():
    with _session_lock:
        _sessions.pop(g.session_token, None)
    return jsonify({"status": "Logged out"})

@app.route("/api/schema", methods=["POST"])
def schema():
	username, password = g.database_credentials

	um = UserManager(root_user=username, root_pass=password, host=DB_HOST, port=DB_PORT)
	with um._connect() as conn, conn.cursor() as cur:
		cur.execute(f"USE {DEFAULT_DB}")
		cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
		tables = [row[0] for row in cur.fetchall()]

		cur.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
		views = [row[0] for row in cur.fetchall()]

		cur.execute("SHOW TRIGGERS")
		triggers = [row[0] for row in cur.fetchall()]

		cur.execute("SHOW PROCEDURE STATUS WHERE Db = %s", (DEFAULT_DB,))
		procedures = [row[1] for row in cur.fetchall()]

	return jsonify({
		"tables": tables,
		"views": views,
		"triggers": triggers,
		"procedures": procedures
	})

@app.route("/api/browse/<table>", methods=["POST"])
def browse(table):
	username, password = g.database_credentials

	um = UserManager(root_user=username, root_pass=password, host=DB_HOST, port=DB_PORT)
	with um._connect() as conn, conn.cursor(dictionary=True) as cur:
		try:
			cur.execute(f"USE {DEFAULT_DB}")
			cur.execute(f"SELECT * FROM `{table}` LIMIT 100")
			rows = cur.fetchall()
			return jsonify(rows)
		except Exception as e:
			return jsonify({"error": str(e)}), 400

@app.route("/api/query", methods=["POST"])
def run_query():
	username, password = g.database_credentials
	sql = request.get_json().get("sql", "").strip()

	if not sql:
		return jsonify({"error": "Query is empty"}), 400

	um = UserManager(root_user=username, root_pass=password, host=DB_HOST, port=DB_PORT)
	with um._connect() as conn:
		is_select = sql.lower().startswith("select")
		cursor_class = conn.cursor(dictionary=True) if is_select else conn.cursor()

		with cursor_class as cur:
			try:
				cur.execute(f"USE {DEFAULT_DB}")
				cur.execute(sql)
				if is_select:
					rows = cur.fetchall()
					return jsonify(rows)
				else:
					conn.commit()
					return jsonify({"status": "OK"})
			except Exception as e:
				return jsonify({"error": str(e)}), 400

@app.route("/api/definition/<table>", methods=["GET"])
def definition(table):
	stmt = get_create_statement(table)
	if not stmt:
		return Response("Table not found in install.sql", status=404)
	return Response(stmt, mimetype="text/plain")

@app.route("/api/view_definition/<name>", methods=["GET"])
def view_definition(name):
	text = get_definition("view", name)
	if text:
		return Response(text, mimetype="text/plain")
	return Response(f"VIEW '{name}' not found.", status=404)

@app.route("/api/procedure_definition/<name>", methods=["GET"])
def procedure_definition(name):
	text = get_definition("procedure", name)
	if text:
		return Response(text, mimetype="text/plain")
	return Response(f"PROCEDURE '{name}' not found.", status=404)

@app.route("/api/trigger_definition/<name>", methods=["GET"])
def trigger_definition(name):
	text = get_definition("trigger", name)
	if text:
		return Response(text, mimetype="text/plain")
	return Response(f"TRIGGER '{name}' not found.", status=404)

@app.route("/api/cli/run", methods=["POST"])
def run_cli_command():
	try:
		data = request.get_json()
		raw = data.get("command", "").strip()

		cmd_parts = raw.split()
		if cmd_parts and cmd_parts[0] == "db137":
			cmd_parts = cmd_parts[1:]

		# Use credentials retained only by the server-side local session.
		username, password = g.database_credentials

		runner = CliRunner()
		with _cli_execution_lock:
			result = runner.invoke(cli, cmd_parts, env={
				"DB_ROOT_USER": username,
				"DB_ROOT_PASS": password,
				"DB_HOST":      DB_HOST,
				"DB_PORT":      str(DB_PORT)
			})

		status = HTTPStatus.OK
		if result.exit_code != 0:
			# treat MySQL “command / access denied” as 403 so the UI can show a clean banner
			if re.search(r"(access|command).*denied|permission", result.output, re.I):
				status = HTTPStatus.FORBIDDEN
			else:
				status = HTTPStatus.BAD_REQUEST

		return Response(result.output, status=status)
	except Exception as e:
		return Response(str(e), status=500)

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=8000, debug=False, threaded=False)
