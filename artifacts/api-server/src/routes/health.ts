import { Router, type IRouter } from "express";
import http from "node:http";
import { HealthCheckResponse } from "@workspace/api-zod";

const router: IRouter = Router();

function pingSimfarm(): Promise<"ok" | "unavailable"> {
  return new Promise((resolve) => {
    const url = process.env["SIMFARM_SIDECAR_URL"] ?? "http://localhost:8000";
    const req = http.get(`${url}/api/levels`, { timeout: 3000 }, (res) => {
      res.resume();
      resolve(res.statusCode === 200 ? "ok" : "unavailable");
    });
    req.on("error", () => resolve("unavailable"));
    req.on("timeout", () => {
      req.destroy();
      resolve("unavailable");
    });
  });
}

router.get("/healthz", async (_req, res) => {
  const simfarmStatus = await pingSimfarm();
  const data = HealthCheckResponse.parse({ status: "ok" });
  res.json({ ...data, simfarm_sidecar: simfarmStatus });
});

export default router;
