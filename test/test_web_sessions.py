"""Offline regressions: the DB boundary is stubbed; no database is contacted."""
import importlib
from pathlib import Path
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'frontend/src/api'))
serve = importlib.import_module('serve')


class WebSessionTests(unittest.TestCase):
    def setUp(self):
        serve.app.config['TESTING'] = True
        self.client = serve.app.test_client()
        serve._sessions.clear()
        no_db = patch('mysql.connector.connect', side_effect=AssertionError('Offline DB boundary'))
        no_db.start()
        self.addCleanup(no_db.stop)

    def login(self):
        with patch.object(serve.UserManager, 'whoami', return_value='demo@localhost'):
            return self.client.post('/api/login', json={'username': 'demo', 'password': 'test-only-password'})

    def test_login_does_not_return_database_credentials(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        token = response.get_json()['token']
        self.assertNotIn('test-only-password', token)
        self.assertNotIn(':', token)

    def test_missing_authorization_is_unauthorized(self):
        response = self.client.post('/api/schema')
        self.assertEqual(response.status_code, 401)

    def test_raw_database_credentials_are_not_a_session(self):
        response = self.client.post('/api/schema', headers={'Authorization': 'demo:test-only-password'})
        self.assertEqual(response.status_code, 401)

    def test_logout_revokes_the_session(self):
        token = self.login().get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        self.assertEqual(self.client.post('/api/logout', headers=headers).status_code, 200)
        self.assertEqual(self.client.post('/api/schema', headers=headers).status_code, 401)

    def test_invalid_login_input_is_rejected_without_database_access(self):
        with patch.object(serve.UserManager, 'whoami', side_effect=AssertionError('DB touched')):
            self.assertEqual(self.client.post('/api/login', json={}).status_code, 400)

    def test_server_expiry_rejects_a_browser_token_at_the_deadline(self):
        with patch.object(serve.time, 'monotonic', return_value=100):
            token = self.login().get_json()['token']
        with patch.object(serve.time, 'monotonic', return_value=100 + serve.SESSION_TTL_SECONDS):
            response = self.client.post('/api/schema', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 401)
        self.assertNotIn(token, serve._sessions)

    def test_session_capacity_is_bounded(self):
        with patch.object(serve, 'MAX_SESSIONS', 0):
            self.assertEqual(self.login().status_code, 503)
        self.assertEqual(len(serve._sessions), 0)

    def test_two_sessions_serialize_process_global_cli_invocations(self):
        tokens = {}
        with patch.object(serve.UserManager, 'whoami', return_value='local-demo'):
            for username in ('alpha', 'beta'):
                result = self.client.post('/api/login', json={'username': username, 'password': 'test-only-password'})
                tokens[username] = result.get_json()['token']
        first_entered, second_started, second_entered, release_first = Event(), Event(), Event(), Event()
        seen = []

        def invoke(_runner, _cli, _args, env):
            seen.append(env['DB_ROOT_USER'])
            if env['DB_ROOT_USER'] == 'alpha':
                first_entered.set()
                if not release_first.wait(3):
                    raise AssertionError('First CLI invocation was not released')
            else:
                second_entered.set()
            return SimpleNamespace(exit_code=0, output='offline command result')

        def request(username):
            with serve.app.test_client() as client:
                if username == 'beta':
                    second_started.set()
                return client.post('/api/cli/run', json={'command': 'db137 db-status'},
                                   headers={'Authorization': f'Bearer {tokens[username]}'})

        with patch.object(serve.CliRunner, 'invoke', invoke), ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(request, 'alpha')
            self.assertTrue(first_entered.wait(1))
            second = pool.submit(request, 'beta')
            try:
                self.assertTrue(second_started.wait(1))
                self.assertFalse(second_entered.wait(0.2), 'Concurrent CliRunner invocations can mix process state')
            finally:
                release_first.set()
            self.assertEqual(first.result(timeout=2).status_code, 200)
            self.assertEqual(second.result(timeout=2).status_code, 200)
        self.assertEqual(seen, ['alpha', 'beta'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
