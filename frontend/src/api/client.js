export const API_BASE = "http://localhost:8000/api";

export function authHeaders() {
	const token = sessionStorage.getItem("token");
	return {
		"Content-Type": "application/json",
		"Authorization": token ? `Bearer ${token}` : ""
	};
}

export async function safeFetch(url, options = {}) {
	const headers = new Headers(authHeaders());
	new Headers(options.headers).forEach((value, name) => headers.set(name, value));
	const authorization = headers.get("Authorization");
	const res = await fetch(url, { ...options, headers });

	if (res.status === 401) {
		// An older request must never erase a session created after it began.
		const current = sessionStorage.getItem("token");
		if (current && authorization === `Bearer ${current}`) {
			sessionStorage.clear();
			window.location.href = "/login";
		}
		throw new Error("Unauthorized");
	}
	if (res.status === 403) throw new Error("Forbidden");

	return res;
}
