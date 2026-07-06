import { Router } from "express";
import { createHash, randomBytes } from "crypto";

const router = Router();

const activeSessions = new Set<string>();

function sha256(value: string): string {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

const AUTH_USERNAME = process.env.AUTH_USERNAME ?? "oeads_admin";
const AUTH_PASSWORD = process.env.AUTH_PASSWORD;
const AUTH_PORTAL_KEY = process.env.AUTH_PORTAL_KEY;

const AUTH_CONFIGURED = !!(AUTH_PASSWORD && AUTH_PORTAL_KEY);
const AUTH_PASSWORD_HASH = AUTH_PASSWORD ? sha256(AUTH_PASSWORD) : null;
const AUTH_PORTAL_KEY_HASH = AUTH_PORTAL_KEY ? sha256(AUTH_PORTAL_KEY) : null;

if (!AUTH_CONFIGURED) {
  console.warn(
    "[auth] WARNING: AUTH_PASSWORD and AUTH_PORTAL_KEY secrets are not set. " +
    "Login endpoint will return 503 until both secrets are configured."
  );
}

router.post("/auth/login", (req, res) => {
  if (!AUTH_CONFIGURED) {
    res.status(503).json({ error: "Authentication not configured — set AUTH_PASSWORD and AUTH_PORTAL_KEY secrets" });
    return;
  }

  const { username, password_hash, portal_key_hash } = req.body as Record<string, string>;

  if (!username || !password_hash || !portal_key_hash) {
    res.status(400).json({ error: "Missing credentials" });
    return;
  }

  const usernameOk = username === AUTH_USERNAME;
  const passwordOk = password_hash === AUTH_PASSWORD_HASH;
  const portalKeyOk = portal_key_hash === AUTH_PORTAL_KEY_HASH;

  if (!usernameOk || !passwordOk || !portalKeyOk) {
    res.status(401).json({ error: "Invalid credentials or portal key" });
    return;
  }

  const token = randomBytes(32).toString("hex");
  activeSessions.add(token);

  res.json({ success: true, token });
});

router.post("/auth/logout", (req, res) => {
  const auth = (req.headers["authorization"] ?? "") as string;
  const token = auth.replace("Bearer ", "").trim();
  activeSessions.delete(token);
  res.json({ success: true });
});

router.get("/auth/verify", (req, res) => {
  const auth = (req.headers["authorization"] ?? "") as string;
  const token = auth.replace("Bearer ", "").trim();
  if (activeSessions.has(token)) {
    res.json({ valid: true });
  } else {
    res.status(401).json({ valid: false });
  }
});

export { activeSessions };
export default router;
