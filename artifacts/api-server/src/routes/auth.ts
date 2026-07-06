import { Router } from "express";
import { createHash, randomBytes } from "crypto";

const router = Router();

const activeSessions = new Set<string>();

function sha256(value: string): string {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

const AUTH_USERNAME = process.env.AUTH_USERNAME;
const AUTH_PASSWORD = process.env.AUTH_PASSWORD;
const AUTH_PORTAL_KEY = process.env.AUTH_PORTAL_KEY;

if (!AUTH_USERNAME || !AUTH_PASSWORD || !AUTH_PORTAL_KEY) {
  throw new Error(
    "OEADS auth is not configured. Set AUTH_USERNAME, AUTH_PASSWORD, and AUTH_PORTAL_KEY environment variables before starting the server."
  );
}

const AUTH_PASSWORD_HASH = sha256(AUTH_PASSWORD);
const AUTH_PORTAL_KEY_HASH = sha256(AUTH_PORTAL_KEY);

router.post("/api/auth/login", (req, res) => {
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

router.post("/api/auth/logout", (req, res) => {
  const auth = (req.headers["authorization"] ?? "") as string;
  const token = auth.replace("Bearer ", "").trim();
  activeSessions.delete(token);
  res.json({ success: true });
});

router.get("/api/auth/verify", (req, res) => {
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
