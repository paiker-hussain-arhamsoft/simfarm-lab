import {
  pgTable,
  text,
  serial,
  boolean,
  timestamp,
  jsonb,
} from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const activityLogsTable = pgTable("activity_logs", {
  id: serial("id").primaryKey(),
  session_id: text("session_id").notNull(),
  ip_address: text("ip_address"),
  user_agent: text("user_agent"),
  action_type: text("action_type").notNull(),
  metadata: jsonb("metadata"),
  flagged: boolean("flagged").notNull().default(false),
  flag_reason: text("flag_reason"),
  flagged_by: text("flagged_by"),
  flagged_at: timestamp("flagged_at", { withTimezone: true }),
  created_at: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const insertActivityLogSchema = createInsertSchema(
  activityLogsTable
).omit({ id: true, created_at: true });
export type InsertActivityLog = z.infer<typeof insertActivityLogSchema>;
export type ActivityLog = typeof activityLogsTable.$inferSelect;
