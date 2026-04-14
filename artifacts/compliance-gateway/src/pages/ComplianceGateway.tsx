import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import {
  ShieldCheck,
  BookOpen,
  UserCheck,
  Scale,
  Fingerprint,
  Lock,
  ClipboardList,
  ArrowRight,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import {
  useRecordConsent,
  useLogActivity,
  useGetSessionStatus,
} from "@workspace/api-client-react";
import { useSessionId } from "@/hooks/useSessionId";
import RestrictedAccess from "./RestrictedAccess";

interface ComplianceItem {
  id: string;
  icon: React.ElementType;
  label: string;
  description: string;
  color: string;
}

const COMPLIANCE_ITEMS: ComplianceItem[] = [
  {
    id: "educational",
    icon: BookOpen,
    label: "Educational purpose only",
    description:
      "I will use this material for education, research, or policy analysis only.",
    color: "text-blue-400",
  },
  {
    id: "responsibility",
    icon: UserCheck,
    label: "Sole responsibility",
    description:
      "I understand I am solely responsible for how I use outputs and tools.",
    color: "text-violet-400",
  },
  {
    id: "lawful",
    icon: Scale,
    label: "Lawful and non-deceptive use",
    description:
      "I will not use this for fraud, impersonation, manipulation, or illegal activity.",
    color: "text-amber-400",
  },
  {
    id: "consent",
    icon: Fingerprint,
    label: "Consent and likeness rights",
    description:
      "I will only use media, voices, and identities when proper consent and rights exist.",
    color: "text-rose-400",
  },
  {
    id: "privacy",
    icon: Lock,
    label: "Data privacy and protection",
    description:
      "I will comply with applicable privacy laws and protect personal data.",
    color: "text-emerald-400",
  },
  {
    id: "audit",
    icon: ClipboardList,
    label: "Audit and governance",
    description:
      "I will maintain transparent records, human review, and abuse reporting controls.",
    color: "text-cyan-400",
  },
];

export default function ComplianceGateway() {
  const [, setLocation] = useLocation();
  const sessionId = useSessionId();

  const [checked, setChecked] = useState<Record<string, boolean>>(
    Object.fromEntries(COMPLIANCE_ITEMS.map((item) => [item.id, false]))
  );

  const recordConsent = useRecordConsent();
  const logActivity = useLogActivity();

  const { data: sessionStatus } = useGetSessionStatus(sessionId, {
    query: { retry: false },
  });

  useEffect(() => {
    logActivity.mutate({
      data: {
        session_id: sessionId,
        action_type: "page_view",
        metadata: { page: "compliance_gate" },
      },
    });
  }, [sessionId]);

  const allChecked = Object.values(checked).every(Boolean);
  const checkedCount = Object.values(checked).filter(Boolean).length;

  const toggle = (id: string) => {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleProceed = () => {
    if (!allChecked) return;

    const consentedItems = COMPLIANCE_ITEMS.map((i) => i.label);

    recordConsent.mutate(
      {
        data: {
          session_id: sessionId,
          user_agent: navigator.userAgent,
          consented_items: consentedItems,
        },
      },
      {
        onSuccess: () => {
          sessionStorage.setItem("compliance_acknowledged", "true");
          setLocation("/access");
        },
      }
    );
  };

  if (sessionStatus?.flagged) {
    return <RestrictedAccess reason={sessionStatus.flag_reason} />;
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/30 flex items-center justify-center">
                <ShieldCheck className="w-8 h-8 text-primary" />
              </div>
              <div className="absolute -inset-1 rounded-2xl bg-primary/5 blur-md -z-10" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight">
            Compliance Gateway
          </h1>
          <p className="mt-2 text-muted-foreground text-sm font-medium uppercase tracking-widest">
            Educational Use Consent &amp; Compliance
          </p>
        </div>

        {/* Main card */}
        <div className="rounded-2xl border border-border bg-card shadow-xl overflow-hidden">
          {/* Card header */}
          <div className="px-6 py-5 border-b border-border bg-muted/40">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-foreground">
                  Compliance Standards Checklist
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  This gate enforces clear user consent, accountability, and
                  legal safeguards. Please acknowledge every requirement before
                  proceeding.
                </p>
              </div>
            </div>
          </div>

          {/* Checklist items */}
          <div className="divide-y divide-border">
            {COMPLIANCE_ITEMS.map((item) => {
              const Icon = item.icon;
              const isChecked = checked[item.id];
              return (
                <label
                  key={item.id}
                  htmlFor={item.id}
                  className={`flex items-start gap-4 px-6 py-4 cursor-pointer transition-colors duration-150 ${
                    isChecked ? "bg-primary/5" : "hover:bg-muted/30"
                  }`}
                >
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                      isChecked
                        ? "bg-primary/15 border border-primary/30"
                        : "bg-muted border border-border"
                    }`}
                  >
                    <Icon
                      className={`w-4 h-4 transition-colors ${
                        isChecked ? "text-primary" : item.color
                      }`}
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <p
                      className={`text-sm font-semibold transition-colors ${
                        isChecked ? "text-primary" : "text-foreground"
                      }`}
                    >
                      {item.label}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                      {item.description}
                    </p>
                  </div>

                  <div className="shrink-0 mt-1">
                    <input
                      id={item.id}
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggle(item.id)}
                      className="sr-only"
                    />
                    <div
                      className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all duration-150 ${
                        isChecked
                          ? "bg-primary border-primary"
                          : "border-border bg-background"
                      }`}
                    >
                      {isChecked && (
                        <svg
                          viewBox="0 0 12 9"
                          className="w-3 h-2.5"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polyline
                            points="1 4.5 4.5 8 11 1"
                            className="text-primary-foreground"
                          />
                        </svg>
                      )}
                    </div>
                  </div>
                </label>
              );
            })}
          </div>

          {/* Footer */}
          <div className="px-6 py-5 border-t border-border bg-muted/20">
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <div className="flex-1 w-full">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs text-muted-foreground">
                    Progress
                  </span>
                  <span className="text-xs font-semibold text-foreground">
                    {checkedCount} / {COMPLIANCE_ITEMS.length}
                  </span>
                </div>
                <div className="w-full h-1.5 bg-border rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-300 ease-out"
                    style={{
                      width: `${(checkedCount / COMPLIANCE_ITEMS.length) * 100}%`,
                    }}
                  />
                </div>
              </div>

              <button
                onClick={handleProceed}
                disabled={!allChecked || recordConsent.isPending}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 shrink-0 ${
                  allChecked && !recordConsent.isPending
                    ? "bg-primary text-primary-foreground hover:opacity-90 active:scale-[0.98] shadow-lg shadow-primary/20"
                    : "bg-muted text-muted-foreground cursor-not-allowed opacity-60"
                }`}
              >
                {recordConsent.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Recording...
                  </>
                ) : (
                  <>
                    Proceed
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Footer note */}
        <p className="text-center text-xs text-muted-foreground mt-4 leading-relaxed">
          By proceeding, you legally acknowledge and agree to the above terms.
          <br />
          All activity is recorded for compliance and audit purposes.
        </p>

        <p className="text-center mt-3">
          <a
            href="/admin"
            className="text-xs text-muted-foreground/50 hover:text-muted-foreground transition-colors"
          >
            Admin
          </a>
        </p>
      </div>
    </div>
  );
}
