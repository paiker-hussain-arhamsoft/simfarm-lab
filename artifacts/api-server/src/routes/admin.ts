import { Router, type IRouter } from "express";
import { db, activityLogsTable } from "@workspace/db";
import { eq, desc, count, sql, and, isNull, not, isNotNull } from "drizzle-orm";
import {
  ListActivityLogsQueryParams,
  FlagActivityParams,
  FlagActivityBody,
  UnflagActivityParams,
  GetSessionStatusParams,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/admin/activity", async (req, res): Promise<void> => {
  const parsed = ListActivityLogsQueryParams.safeParse(req.query);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const { page, limit, flagged, session_id, action_type } = parsed.data;
  const offset = (page - 1) * limit;

  const conditions = [];
  if (flagged !== undefined) {
    conditions.push(eq(activityLogsTable.flagged, flagged));
  }
  if (session_id) {
    conditions.push(eq(activityLogsTable.session_id, session_id));
  }
  if (action_type) {
    conditions.push(eq(activityLogsTable.action_type, action_type));
  }

  const where = conditions.length > 0 ? and(...conditions) : undefined;

  const [items, [{ total }]] = await Promise.all([
    db
      .select()
      .from(activityLogsTable)
      .where(where)
      .orderBy(desc(activityLogsTable.created_at))
      .limit(limit)
      .offset(offset),
    db
      .select({ total: count() })
      .from(activityLogsTable)
      .where(where),
  ]);

  res.json({ items, total, page, limit });
});

router.patch("/admin/activity/:id/flag", async (req, res): Promise<void> => {
  const params = FlagActivityParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const body = FlagActivityBody.safeParse(req.body);
  if (!body.success) {
    res.status(400).json({ error: body.error.message });
    return;
  }

  const [log] = await db
    .update(activityLogsTable)
    .set({
      flagged: true,
      flag_reason: body.data.flag_reason,
      flagged_by: body.data.flagged_by ?? "admin",
      flagged_at: new Date(),
    })
    .where(eq(activityLogsTable.id, params.data.id))
    .returning();

  if (!log) {
    res.status(404).json({ error: "Activity log not found" });
    return;
  }

  req.log.info({ id: params.data.id }, "Activity flagged");
  res.json(log);
});

router.delete("/admin/activity/:id/flag", async (req, res): Promise<void> => {
  const params = UnflagActivityParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [log] = await db
    .update(activityLogsTable)
    .set({
      flagged: false,
      flag_reason: null,
      flagged_by: null,
      flagged_at: null,
    })
    .where(eq(activityLogsTable.id, params.data.id))
    .returning();

  if (!log) {
    res.status(404).json({ error: "Activity log not found" });
    return;
  }

  req.log.info({ id: params.data.id }, "Activity unflagged");
  res.json(log);
});

router.get(
  "/admin/session/:sessionId/status",
  async (req, res): Promise<void> => {
    const params = GetSessionStatusParams.safeParse(req.params);
    if (!params.success) {
      res.status(400).json({ error: params.error.message });
      return;
    }

    const flaggedEntry = await db
      .select()
      .from(activityLogsTable)
      .where(
        and(
          eq(activityLogsTable.session_id, params.data.sessionId),
          eq(activityLogsTable.flagged, true)
        )
      )
      .limit(1);

    if (flaggedEntry.length > 0) {
      const entry = flaggedEntry[0];
      res.json({
        session_id: params.data.sessionId,
        flagged: true,
        flag_reason: entry.flag_reason,
        flagged_at: entry.flagged_at?.toISOString() ?? null,
      });
      return;
    }

    res.json({
      session_id: params.data.sessionId,
      flagged: false,
      flag_reason: null,
      flagged_at: null,
    });
  }
);

router.get("/admin/stats", async (_req, res): Promise<void> => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const [
    [{ total_events }],
    [{ flagged_sessions }],
    [{ total_sessions }],
    [{ consents_today }],
    [{ events_today }],
  ] = await Promise.all([
    db.select({ total_events: count() }).from(activityLogsTable),
    db
      .select({ flagged_sessions: count() })
      .from(activityLogsTable)
      .where(eq(activityLogsTable.flagged, true)),
    db
      .select({ total_sessions: sql<number>`COUNT(DISTINCT ${activityLogsTable.session_id})` })
      .from(activityLogsTable),
    db
      .select({ consents_today: count() })
      .from(activityLogsTable)
      .where(
        and(
          eq(activityLogsTable.action_type, "consent_acknowledged"),
          sql`${activityLogsTable.created_at} >= ${today.toISOString()}`
        )
      ),
    db
      .select({ events_today: count() })
      .from(activityLogsTable)
      .where(
        sql`${activityLogsTable.created_at} >= ${today.toISOString()}`
      ),
  ]);

  res.json({
    total_sessions: Number(total_sessions),
    total_events: Number(total_events),
    flagged_sessions: Number(flagged_sessions),
    consents_today: Number(consents_today),
    events_today: Number(events_today),
  });
});

export default router;
