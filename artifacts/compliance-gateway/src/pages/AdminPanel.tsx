import { useState } from "react";
import {
  ShieldCheck,
  Users,
  Activity,
  Flag,
  AlertTriangle,
  CalendarDays,
  Search,
  X,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Eye,
  Filter,
} from "lucide-react";
import {
  useGetActivityStats,
  useListActivityLogs,
  useFlagActivity,
  useUnflagActivity,
  getListActivityLogsQueryKey,
  getGetActivityStatsQueryKey,
} from "@workspace/api-client-react";
import { useQueryClient } from "@tanstack/react-query";
import type { ActivityLog } from "@workspace/api-client-react";

function StatCard({
  icon: Icon,
  label,
  value,
  accent,
}: {
  icon: React.ElementType;
  label: string;
  value: number | undefined;
  accent: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${accent}`}>
          <Icon className="w-4 h-4" />
        </div>
        <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
          {label}
        </span>
      </div>
      <p className="text-3xl font-bold text-foreground">
        {value ?? <span className="text-muted-foreground text-xl">—</span>}
      </p>
    </div>
  );
}

function FlagModal({
  onConfirm,
  onCancel,
  isPending,
}: {
  onConfirm: (reason: string) => void;
  onCancel: () => void;
  isPending: boolean;
}) {
  const [reason, setReason] = useState("");
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card shadow-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 rounded-xl bg-destructive/10 border border-destructive/20 flex items-center justify-center">
            <Flag className="w-4 h-4 text-destructive" />
          </div>
          <h2 className="text-base font-semibold text-foreground">
            Flag Activity
          </h2>
        </div>
        <p className="text-sm text-muted-foreground mb-4">
          Provide a reason for flagging this activity. The session will be
          restricted once flagged.
        </p>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Describe why this activity is being flagged..."
          rows={3}
          className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 mb-4"
        />
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2.5 rounded-xl border border-border text-sm font-medium text-muted-foreground hover:bg-muted/40 transition-colors"
          >
            Cancel
          </button>
          <button
            disabled={!reason.trim() || isPending}
            onClick={() => onConfirm(reason.trim())}
            className="flex-1 px-4 py-2.5 rounded-xl bg-destructive text-destructive-foreground text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isPending ? "Flagging..." : "Flag Session"}
          </button>
        </div>
      </div>
    </div>
  );
}

function ActionTypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    consent_acknowledged: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    page_view: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    access_granted: "bg-violet-500/10 text-violet-400 border-violet-500/20",
  };
  const cls = colors[type] ?? "bg-muted text-muted-foreground border-border";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md border text-xs font-medium ${cls}`}>
      {type.replace(/_/g, " ")}
    </span>
  );
}

export default function AdminPanel() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const [filterFlagged, setFilterFlagged] = useState<boolean | undefined>(undefined);
  const [sessionSearch, setSessionSearch] = useState("");
  const [flagTarget, setFlagTarget] = useState<ActivityLog | null>(null);

  const LIMIT = 20;

  const { data: stats, refetch: refetchStats } = useGetActivityStats();

  const { data: logs, isLoading } = useListActivityLogs(
    {
      page,
      limit: LIMIT,
      ...(filterFlagged !== undefined ? { flagged: filterFlagged } : {}),
      ...(sessionSearch.trim() ? { session_id: sessionSearch.trim() } : {}),
    },
    { query: { refetchInterval: 15000 } }
  );

  const flagMutation = useFlagActivity({
    mutation: {
      onSuccess: () => {
        qc.invalidateQueries({ queryKey: getListActivityLogsQueryKey() });
        qc.invalidateQueries({ queryKey: getGetActivityStatsQueryKey() });
        setFlagTarget(null);
      },
    },
  });

  const unflagMutation = useUnflagActivity({
    mutation: {
      onSuccess: () => {
        qc.invalidateQueries({ queryKey: getListActivityLogsQueryKey() });
        qc.invalidateQueries({ queryKey: getGetActivityStatsQueryKey() });
      },
    },
  });

  const totalPages = logs ? Math.ceil(logs.total / LIMIT) : 1;

  const refresh = () => {
    qc.invalidateQueries({ queryKey: getListActivityLogsQueryKey() });
    qc.invalidateQueries({ queryKey: getGetActivityStatsQueryKey() });
  };

  return (
    <div className="min-h-screen bg-background">
      {flagTarget && (
        <FlagModal
          onCancel={() => setFlagTarget(null)}
          isPending={flagMutation.isPending}
          onConfirm={(reason) =>
            flagMutation.mutate({
              id: flagTarget.id,
              data: { flag_reason: reason, flagged_by: "admin" },
            })
          }
        />
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/30 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">
                Compliance Admin
              </h1>
              <p className="text-xs text-muted-foreground">
                Activity monitoring &amp; session governance
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={refresh}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border bg-card text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Refresh
            </button>
            <a
              href="/"
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border bg-card text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
            >
              <Eye className="w-3.5 h-3.5" />
              View Gate
            </a>
          </div>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
          <StatCard
            icon={Users}
            label="Total Sessions"
            value={stats?.total_sessions}
            accent="bg-blue-500/10 text-blue-400"
          />
          <StatCard
            icon={Activity}
            label="Total Events"
            value={stats?.total_events}
            accent="bg-violet-500/10 text-violet-400"
          />
          <StatCard
            icon={AlertTriangle}
            label="Flagged Sessions"
            value={stats?.flagged_sessions}
            accent="bg-destructive/10 text-destructive"
          />
          <StatCard
            icon={ShieldCheck}
            label="Consents Today"
            value={stats?.consents_today}
            accent="bg-emerald-500/10 text-emerald-400"
          />
          <StatCard
            icon={CalendarDays}
            label="Events Today"
            value={stats?.events_today}
            accent="bg-amber-500/10 text-amber-400"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="w-3.5 h-3.5" />
            Filters:
          </div>
          <button
            onClick={() => { setFilterFlagged(undefined); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              filterFlagged === undefined
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border text-muted-foreground hover:text-foreground hover:bg-muted/40"
            }`}
          >
            All
          </button>
          <button
            onClick={() => { setFilterFlagged(false); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              filterFlagged === false
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                : "border-border text-muted-foreground hover:text-foreground hover:bg-muted/40"
            }`}
          >
            Clear
          </button>
          <button
            onClick={() => { setFilterFlagged(true); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              filterFlagged === true
                ? "bg-destructive/20 text-destructive border-destructive/30"
                : "border-border text-muted-foreground hover:text-foreground hover:bg-muted/40"
            }`}
          >
            Flagged only
          </button>

          <div className="flex items-center gap-2 flex-1 min-w-0 max-w-xs ml-auto">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <input
                type="text"
                value={sessionSearch}
                onChange={(e) => { setSessionSearch(e.target.value); setPage(1); }}
                placeholder="Search session ID..."
                className="w-full pl-8 pr-3 py-1.5 rounded-lg border border-border bg-card text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              {sessionSearch && (
                <button
                  onClick={() => { setSessionSearch(""); setPage(1); }}
                  className="absolute right-2 top-1/2 -translate-y-1/2"
                >
                  <X className="w-3 h-3 text-muted-foreground hover:text-foreground" />
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Activity log table */}
        <div className="rounded-2xl border border-border bg-card overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <p className="text-sm font-semibold text-foreground">
              Activity Log
            </p>
            <p className="text-xs text-muted-foreground">
              {logs ? `${logs.total} records` : "Loading..."}
            </p>
          </div>

          {isLoading ? (
            <div className="py-16 text-center text-sm text-muted-foreground">
              Loading activity logs...
            </div>
          ) : !logs?.items.length ? (
            <div className="py-16 text-center text-sm text-muted-foreground">
              No activity logs found.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      ID
                    </th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Session
                    </th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Action
                    </th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      IP
                    </th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Time
                    </th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Status
                    </th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {logs.items.map((log) => (
                    <tr
                      key={log.id}
                      className={`hover:bg-muted/20 transition-colors ${
                        log.flagged ? "bg-destructive/5" : ""
                      }`}
                    >
                      <td className="px-4 py-3 text-xs text-muted-foreground font-mono">
                        #{log.id}
                      </td>
                      <td className="px-4 py-3">
                        <span className="font-mono text-xs text-primary/80 truncate block max-w-[120px]" title={log.session_id}>
                          {log.session_id.slice(0, 8)}…
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <ActionTypeBadge type={log.action_type} />
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground font-mono">
                        {log.ip_address ?? "—"}
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        {log.flagged ? (
                          <div>
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-destructive/10 text-destructive border border-destructive/20 text-xs font-medium">
                              <Flag className="w-3 h-3" />
                              Flagged
                            </span>
                            {log.flag_reason && (
                              <p className="text-xs text-muted-foreground mt-0.5 max-w-[140px] truncate" title={log.flag_reason}>
                                {log.flag_reason}
                              </p>
                            )}
                          </div>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium">
                            Clear
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {log.flagged ? (
                          <button
                            onClick={() => unflagMutation.mutate({ id: log.id })}
                            disabled={unflagMutation.isPending}
                            className="text-xs text-muted-foreground hover:text-foreground border border-border px-2.5 py-1 rounded-lg hover:bg-muted/40 transition-colors disabled:opacity-50"
                          >
                            Unflag
                          </button>
                        ) : (
                          <button
                            onClick={() => setFlagTarget(log)}
                            className="text-xs text-destructive hover:text-destructive/80 border border-destructive/20 px-2.5 py-1 rounded-lg hover:bg-destructive/10 transition-colors"
                          >
                            Flag
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {logs && logs.total > LIMIT && (
            <div className="px-5 py-4 border-t border-border flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                Page {page} of {totalPages}
              </p>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  Previous
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Next
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
