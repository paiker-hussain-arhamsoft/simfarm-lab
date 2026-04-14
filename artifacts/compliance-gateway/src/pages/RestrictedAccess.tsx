import { ShieldX, ArrowLeft } from "lucide-react";
import { useLocation } from "wouter";

interface Props {
  reason?: string | null;
}

export default function RestrictedAccess({ reason }: Props) {
  const [, setLocation] = useLocation();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-lg text-center">
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-destructive/10 border-2 border-destructive/40 flex items-center justify-center">
              <ShieldX className="w-10 h-10 text-destructive" />
            </div>
            <div className="absolute -inset-2 rounded-full bg-destructive/5 blur-lg -z-10" />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-foreground tracking-tight">
          Access Restricted
        </h1>
        <p className="mt-3 text-muted-foreground max-w-sm mx-auto text-sm leading-relaxed">
          Your session has been flagged by the compliance system. Access to this
          platform has been temporarily suspended pending review.
        </p>

        {reason && (
          <div className="mt-6 rounded-xl border border-destructive/20 bg-destructive/5 px-5 py-4 text-left">
            <p className="text-xs font-semibold text-destructive uppercase tracking-wider mb-1">
              Flag Reason
            </p>
            <p className="text-sm text-muted-foreground">{reason}</p>
          </div>
        )}

        <div className="mt-6 rounded-2xl border border-border bg-card p-5 text-left text-sm text-muted-foreground leading-relaxed">
          <p>
            If you believe this is an error, please contact the system
            administrator with your session reference for further assistance.
          </p>
        </div>

        <button
          onClick={() => {
            sessionStorage.clear();
            setLocation("/");
          }}
          className="mt-6 flex items-center gap-2 mx-auto text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Start a new session
        </button>
      </div>
    </div>
  );
}
