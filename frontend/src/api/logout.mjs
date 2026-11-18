/** Clear this browser session before awaiting the old server revocation. */
export function logoutSession({ storage = globalThis.sessionStorage, request = globalThis.fetch, endpoint } = {}) {
 const token = storage.getItem('token');
 const headers = { 'Content-Type': 'application/json', Authorization: token ? `Bearer ${token}` : '' };
 storage.clear();
 // Completion must never mutate storage: another login may already have begun.
 return Promise.resolve().then(() => request(endpoint, { method: 'POST', headers })).then(() => undefined, () => undefined);
}
