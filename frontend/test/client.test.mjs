import test, { afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { safeFetch } from '../src/api/client.js';

const originals = { fetch: globalThis.fetch, sessionStorage: globalThis.sessionStorage, window: globalThis.window };
afterEach(() => Object.assign(globalThis, originals));
function browser() {
 const values = new Map([['token', 'old-session'], ['username', 'demo']]);
 globalThis.sessionStorage = { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value), clear: () => values.clear() };
 globalThis.window = { location: { href: '/browse' } };
 return globalThis.sessionStorage;
}

test('definition requests include the active session without explicit options', async () => {
 browser(); let sent;
 globalThis.fetch = async (_url, options) => { sent = new Headers(options.headers); return { status: 200 }; };
 await safeFetch('/api/definition/demo');
 assert.equal(sent.get('Authorization'), 'Bearer old-session');
});

test('a delayed unauthorized response preserves a newer login', async () => {
 const storage = browser();
 globalThis.fetch = async () => { storage.setItem('token', 'new-session'); return { status: 401 }; };
 await assert.rejects(safeFetch('/api/schema'), /Unauthorized/);
 assert.equal(storage.getItem('token'), 'new-session');
 assert.equal(window.location.href, '/browse');
});

test('the rejected current session is cleared and redirected', async () => {
 const storage = browser(); globalThis.fetch = async () => ({ status: 401 });
 await assert.rejects(safeFetch('/api/schema'), /Unauthorized/);
 assert.equal(storage.getItem('token'), null);
 assert.equal(window.location.href, '/login');
});

test('database permission denial preserves the authenticated session', async () => {
 const storage = browser(); globalThis.fetch = async () => ({ status: 403 });
 await assert.rejects(safeFetch('/api/query'), /Forbidden/);
 assert.equal(storage.getItem('token'), 'old-session');
 assert.equal(window.location.href, '/browse');
});
