import { Router, type IRouter } from "express";
import { db, activityLogsTable } from "@workspace/db";
import {
  RecordConsentBody,
  LogActivityBody,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.post("/activity/consent", async (req, res): Promise<void> => {
  const parsed = RecordConsentBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const ip =
    (req.headers["x-forwarded-for"] as string)?.split(",")[0]?.trim() ||
    req.socket.remoteAddress ||
    null;

  const [log] = await db
    .insert(activityLogsTable)
    .values({
      session_id: parsed.data.session_id,
      ip_address: ip,
      user_agent: parsed.data.user_agent ?? req.headers["user-agent"] ?? null,
      action_type: "consent_acknowledged",
      metadata: { consented_items: parsed.data.consented_items },
      flagged: false,
    })
    .returning();

  req.log.info(
    { session_id: parsed.data.session_id, id: log.id },
    "Consent recorded"
  );
  res.status(201).json(log);
});

router.post("/activity/log", async (req, res): Promise<void> => {
  const parsed = LogActivityBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const ip =
    (req.headers["x-forwarded-for"] as string)?.split(",")[0]?.trim() ||
    req.socket.remoteAddress ||
    null;

  const [log] = await db
    .insert(activityLogsTable)
    .values({
      session_id: parsed.data.session_id,
      ip_address: ip,
      user_agent: req.headers["user-agent"] ?? null,
      action_type: parsed.data.action_type,
      metadata: parsed.data.metadata ?? null,
      flagged: false,
    })
    .returning();

  res.status(201).json(log);
});

export default router;
