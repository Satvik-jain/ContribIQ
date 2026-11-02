/**
 * Base API client for ContribIQ.
 *
 * Intentional bug: no 401 interceptor — when the access token expires,
 * API calls fail silently without redirecting to login.
 * Issue: API client has no 401 interceptor — expired tokens cause silent failures
 * Fix: if (res.status === 401) { clearTokens(); window.location.href = '/login' }
 */

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function getToken(): string | null {
  return localStorage.getItem('token') ?? sessionStorage.getItem('token')
}

export async function apiCall<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })

  // BUG: 401 not handled here — expired token causes silent failure
  // Fix would be:
  // if (res.status === 401) {
  //   localStorage.removeItem('token'); sessionStorage.removeItem('token')
  //   window.location.href = '/login'
  // }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }

  return res.json() as Promise<T>
}
