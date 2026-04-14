import { useEffect } from "react";
import { useLocation } from "wouter";
import { ShieldCheck, CheckCircle2, ArrowLeft } from "lucide-react";

export default function AccessGranted() {
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (sessionStorage.getItem("compliance_acknowledged") !== "true") {
      setLocation("/");
    }
  }, [setLocation]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-lg text-center">
        {/* Animated success icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-emerald-500/10 border-2 border-emerald-500/40 flex items-center justify-center">
              <CheckCircle2 className="w-10 h-10 text-emerald-400" />
            </div>
            <div className="absolute -inset-2 rounded-full bg-emerald-500/5 blur-lg -z-10" />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-foreground tracking-tight">
          Access Granted
        </h1>
        <p className="mt-3 text-muted-foreground max-w-sm mx-auto text-sm leading-relaxed">
          You have acknowledged all compliance requirements. You are now
          authorized to proceed with educational use of this material.
        </p>

        {/* Summary box */}
        <div className="mt-8 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-6 text-left">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
              Consent Record
            </span>
          </div>
          <ul className="space-y-2 text-sm text-muted-foreground">
            {[
              "Educational purpose only",
              "Sole responsibility acknowledged",
              "Lawful and non-deceptive use",
              "Consent and likeness rights confirmed",
              "Data privacy and protection",
              "Audit and governance",
            ].map((item) => (
              <li key={item} className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-muted-foreground/70 border-t border-emerald-500/10 pt-3">
            Consented on: {new Date().toLocaleString()} &mdash; Session only
          </p>
        </div>

        <button
          onClick={() => {
            sessionStorage.removeItem("compliance_acknowledged");
            setLocation("/");
          }}
          className="mt-6 flex items-center gap-2 mx-auto text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Return to compliance gate
        </button>
      </div>
    </div>
  );
}
