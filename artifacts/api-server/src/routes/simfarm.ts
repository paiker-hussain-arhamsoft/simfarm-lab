import { Router } from "express";
import http from "node:http";
import https from "node:https";
import { URL } from "node:url";

const router = Router();

const SIMFARM_SIDECAR_URL = process.env["SIMFARM_SIDECAR_URL"] ?? "http://localhost:8000";

function proxyRequest(
  targetUrl: string,
  req: import("express").Request,
  res: import("express").Response,
): void {
  let url: URL;
  try {
    url = new URL(targetUrl);
  } catch {
    res.status(502).json({ error: "SimFarm sidecar URL is misconfigured" });
    return;
  }

  const isHttps = url.protocol === "https:";
  const transport = isHttps ? https : http;

  const options: http.RequestOptions = {
    hostname: url.hostname,
    port: url.port || (isHttps ? 443 : 80),
    path: url.pathname + (url.search || ""),
    method: req.method,
    headers: {
      ...req.headers,
      host: url.hostname + (url.port ? `:${url.port}` : ""),
    },
  };

  const proxyReq = transport.request(options, (proxyRes) => {
    res.status(proxyRes.statusCode ?? 502);
    for (const [key, value] of Object.entries(proxyRes.headers)) {
      if (value !== undefined) {
        res.setHeader(key, value);
      }
    }
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.on("error", (err) => {
    console.error("[simfarm proxy] sidecar unreachable:", err.message);
    if (!res.headersSent) {
      res.status(503).json({
        error: "SimFarm sidecar is unavailable",
        detail: err.message,
      });
    }
  });

  proxyReq.setTimeout(30_000, () => {
    proxyReq.destroy();
    if (!res.headersSent) {
      res.status(504).json({ error: "SimFarm sidecar timed out" });
    }
  });

  if (req.body && req.method !== "GET" && req.method !== "HEAD") {
    const body = JSON.stringify(req.body);
    proxyReq.setHeader("content-type", "application/json");
    proxyReq.setHeader("content-length", Buffer.byteLength(body));
    proxyReq.write(body);
  }

  proxyReq.end();
}

router.all(/^\/simfarm(\/.*)?$/, (req, res) => {
  const suffix = req.path.replace(/^\/simfarm/, "") || "/";
  const qs = req.url.includes("?") ? req.url.slice(req.url.indexOf("?")) : "";
  const target = `${SIMFARM_SIDECAR_URL}/api${suffix}${qs}`;
  proxyRequest(target, req, res);
});

export default router;
