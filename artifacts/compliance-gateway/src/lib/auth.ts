const TOKEN_KEY = "oeads_auth_token";
const PORTAL_KEY = "oeads_portal_key";

export async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function getAuthToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

export function getPortalKeyHash(): string | null {
  return localStorage.getItem(PORTAL_KEY);
}

export function setPortalKeyHash(hash: string): void {
  localStorage.setItem(PORTAL_KEY, hash);
}

export function clearPortalKeyHash(): void {
  localStorage.removeItem(PORTAL_KEY);
}

export function isAuthenticated(): boolean {
  return !!getAuthToken() && !!getPortalKeyHash();
}

export async function mountPortalKey(rawKey: string): Promise<void> {
  const hash = await sha256(rawKey);
  setPortalKeyHash(hash);
}

export function unmountPortalKey(): void {
  clearPortalKeyHash();
  clearAuthToken();
}

export async function login(
  username: string,
  password: string,
  portalKeyRaw: string
): Promise<{ success: boolean; token?: string; error?: string }> {
  try {
    const password_hash = await sha256(password);
    const portal_key_hash = await sha256(portalKeyRaw);

    const base = import.meta.env.BASE_URL?.replace(/\/$/, "") ?? "";
    const res = await fetch(`${base}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password_hash, portal_key_hash }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      return { success: false, error: (data as { error?: string }).error ?? "Authentication failed" };
    }

    const data = (await res.json()) as { token: string };
    return { success: true, token: data.token };
  } catch {
    return { success: false, error: "Network error — server unreachable" };
  }
}

export async function logout(): Promise<void> {
  const token = getAuthToken();
  if (token) {
    const base = import.meta.env.BASE_URL?.replace(/\/$/, "") ?? "";
    await fetch(`${base}/api/auth/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => {});
  }
  clearAuthToken();
  clearPortalKeyHash();
}
