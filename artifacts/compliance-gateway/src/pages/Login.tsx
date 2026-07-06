import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import {
  Shield,
  Lock,
  KeyRound,
  Eye,
  EyeOff,
  Usb,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  LogIn,
  FileText,
  ScrollText,
  BookOpen,
  Unlink,
} from "lucide-react";
import {
  login,
  mountPortalKey,
  unmountPortalKey,
  isAuthenticated,
  getPortalKeyHash,
  setAuthToken,
} from "@/lib/auth";

const AGENCIES = [
  { abbr: "FedRAMP", full: "Federal Risk & Authorization Management Program", color: "text-blue-400" },
  { abbr: "DoD", full: "Department of Defense", color: "text-blue-300" },
  { abbr: "CISA", full: "Cybersecurity & Infrastructure Security Agency (US)", color: "text-cyan-400" },
  { abbr: "NCSC", full: "National Cyber Security Centre (UK)", color: "text-blue-400" },
  { abbr: "FEC", full: "Federal Election Commission", color: "text-violet-400" },
  { abbr: "TCPA", full: "Telephone Consumer Protection Act", color: "text-orange-400" },
  { abbr: "CFAA", full: "Computer Fraud & Abuse Act", color: "text-red-400" },
  { abbr: "ITU", full: "UN International Telecommunication Union", color: "text-green-400" },
  { abbr: "INTERPOL", full: "International Criminal Police Organization", color: "text-yellow-400" },
  { abbr: "ENISA", full: "EU Agency for Cybersecurity", color: "text-blue-400" },
  { abbr: "CERT", full: "National CERT/CSIRT Network", color: "text-orange-300" },
  { abbr: "GRC", full: "Governance, Risk & Compliance Framework", color: "text-violet-300" },
];

export default function Login() {
  const [, navigate] = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [portalKeyInput, setPortalKeyInput] = useState("");
  const [portalMounted, setPortalMounted] = useState(false);
  const [mounting, setMounting] = useState(false);
  const [loggingIn, setLoggingIn] = useState(false);
  const [error, setError] = useState("");
  const [showMountField, setShowMountField] = useState(false);

  useEffect(() => {
    setPortalMounted(!!getPortalKeyHash());
    if (isAuthenticated()) {
      navigate("/");
    }
  }, [navigate]);

  async function handleMountKey() {
    if (!portalKeyInput.trim()) return;
    setMounting(true);
    setError("");
    try {
      await mountPortalKey(portalKeyInput.trim());
      setPortalMounted(true);
      setPortalKeyInput("");
      setShowMountField(false);
    } catch {
      setError("Failed to mount portal key.");
    } finally {
      setMounting(false);
    }
  }

  function handleUnmount() {
    unmountPortalKey();
    setPortalMounted(false);
    setShowMountField(false);
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (!portalMounted) {
      setError("Portal key must be mounted before authenticating.");
      return;
    }
    setLoggingIn(true);
    setError("");
    try {
      const storedHash = getPortalKeyHash() ?? "";
      const { sha256 } = await import("@/lib/auth");
      const password_hash = await sha256(password);
      const base = import.meta.env.BASE_URL?.replace(/\/$/, "") ?? "";
      const res = await fetch(`${base}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password_hash, portal_key_hash: storedHash }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError((data as { error?: string }).error ?? "Authentication failed.");
        return;
      }
      const data = (await res.json()) as { token: string };
      setAuthToken(data.token);
      navigate("/");
    } catch {
      setError("Network error — server unreachable.");
    } finally {
      setLoggingIn(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#080c14] flex flex-col">
      {/* Classification Banner */}
      <div className="bg-red-700 text-white text-center py-1.5 text-xs font-bold tracking-[0.25em] uppercase">
        TOP SECRET // AUTHORIZED PERSONNEL ONLY // OEADS ORGANIZATIONAL SYSTEM
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-4 py-8">

        {/* Logo + Title Block */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-blue-600/20 border-2 border-blue-500/40 flex items-center justify-center">
              <Shield className="w-6 h-6 text-blue-400" />
            </div>
            <div className="text-left">
              <div className="text-white font-black text-2xl tracking-widest">OEADS</div>
              <div className="text-slate-400 text-[10px] tracking-[0.2em] uppercase">
                Orchestrated Educational AI Deployment System
              </div>
            </div>
          </div>
          <div className="flex items-center justify-center gap-2 mt-2">
            <span className="px-2 py-0.5 rounded bg-red-900/60 border border-red-700/50 text-red-300 text-[9px] font-bold tracking-widest uppercase">Confidential</span>
            <span className="px-2 py-0.5 rounded bg-orange-900/60 border border-orange-700/50 text-orange-300 text-[9px] font-bold tracking-widest uppercase">Top Secret</span>
            <span className="px-2 py-0.5 rounded bg-green-900/60 border border-green-700/50 text-green-300 text-[9px] font-bold tracking-widest uppercase">Secure Site</span>
            <span className="px-2 py-0.5 rounded bg-violet-900/60 border border-violet-700/50 text-violet-300 text-[9px] font-bold tracking-widest uppercase">GRC Compliant</span>
          </div>
          <div className="mt-3 text-[9px] text-slate-500 tracking-wider max-w-sm mx-auto">
            Protected under the U.S. Patent Act (35 U.S.C.) &bull; Unauthorized access violates 18 U.S.C. &sect; 1030 (CFAA)
          </div>
        </div>

        {/* Agency Badges */}
        <div className="flex flex-wrap justify-center gap-1.5 mb-8 max-w-xl">
          {AGENCIES.map((a) => (
            <span
              key={a.abbr}
              title={a.full}
              className={`px-2 py-0.5 rounded text-[9px] font-semibold tracking-widest uppercase border border-slate-700/50 bg-slate-800/60 ${a.color} cursor-default`}
            >
              {a.abbr}
            </span>
          ))}
        </div>

        {/* Login Card */}
        <div className="w-full max-w-md">
          <div className="bg-slate-900/80 border border-slate-700/60 rounded-xl overflow-hidden shadow-2xl shadow-black/60">

            {/* Card header */}
            <div className="border-b border-slate-700/50 px-6 py-4 flex items-center gap-3">
              <Lock className="w-4 h-4 text-blue-400" />
              <span className="text-slate-200 text-sm font-semibold tracking-widest uppercase">Secure Authentication</span>
            </div>

            <div className="px-6 py-6 space-y-5">

              {/* Portal Key Section */}
              <div className={`rounded-lg border p-4 ${portalMounted ? "border-green-700/50 bg-green-950/20" : "border-orange-700/50 bg-orange-950/20"}`}>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <Usb className={`w-4 h-4 ${portalMounted ? "text-green-400" : "text-orange-400"}`} />
                    <span className="text-xs font-semibold text-slate-300 tracking-widest uppercase">Portal Security Key</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    {portalMounted ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-green-400" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-orange-400" />
                    )}
                    <span className={`text-[10px] font-bold tracking-widest uppercase ${portalMounted ? "text-green-400" : "text-orange-400"}`}>
                      {portalMounted ? "Mounted" : "Not Mounted"}
                    </span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-500 mb-3">
                  {portalMounted
                    ? "Security key is active in this browser session. Unmounting will require full re-authentication."
                    : "A portal key must be mounted before you can authenticate. Enter your organizational key below."}
                </p>

                {portalMounted ? (
                  <button
                    type="button"
                    onClick={handleUnmount}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded text-[11px] font-semibold text-orange-400 border border-orange-700/50 bg-orange-950/30 hover:bg-orange-900/40 transition-colors"
                  >
                    <Unlink className="w-3 h-3" />
                    Unmount Key
                  </button>
                ) : (
                  <div>
                    {!showMountField ? (
                      <button
                        type="button"
                        onClick={() => setShowMountField(true)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded text-[11px] font-semibold text-blue-400 border border-blue-700/50 bg-blue-950/30 hover:bg-blue-900/40 transition-colors"
                      >
                        <KeyRound className="w-3 h-3" />
                        Mount Portal Key
                      </button>
                    ) : (
                      <div className="flex gap-2">
                        <input
                          type="password"
                          value={portalKeyInput}
                          onChange={(e) => setPortalKeyInput(e.target.value)}
                          onKeyDown={(e) => e.key === "Enter" && handleMountKey()}
                          placeholder="Enter portal key..."
                          className="flex-1 bg-slate-800 border border-slate-600/50 rounded px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
                          autoFocus
                        />
                        <button
                          type="button"
                          onClick={handleMountKey}
                          disabled={mounting || !portalKeyInput.trim()}
                          className="px-3 py-1.5 rounded text-[11px] font-semibold bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white transition-colors flex items-center gap-1"
                        >
                          {mounting ? <Loader2 className="w-3 h-3 animate-spin" /> : <KeyRound className="w-3 h-3" />}
                          Mount
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Login Form */}
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 tracking-widest uppercase mb-1.5">
                    Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Organizational username"
                    autoComplete="username"
                    className="w-full bg-slate-800 border border-slate-600/50 rounded-lg px-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/60 transition-colors"
                    required
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 tracking-widest uppercase mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Secure access password"
                      autoComplete="current-password"
                      className="w-full bg-slate-800 border border-slate-600/50 rounded-lg px-4 py-2.5 pr-10 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/60 transition-colors"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((v) => !v)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="flex items-start gap-2 p-3 rounded-lg bg-red-950/40 border border-red-700/40">
                    <AlertTriangle className="w-3.5 h-3.5 text-red-400 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-red-300">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loggingIn || !username || !password || !portalMounted}
                  className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors"
                >
                  {loggingIn ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <LogIn className="w-4 h-4" />
                  )}
                  {loggingIn ? "Authenticating..." : "Authenticate"}
                </button>
              </form>

              {/* Warning */}
              <div className="flex items-start gap-2 p-3 rounded-lg bg-amber-950/20 border border-amber-700/30">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400 mt-0.5 flex-shrink-0" />
                <p className="text-[10px] text-amber-300/80 leading-relaxed">
                  Unauthorized access attempts are logged, traced, and reported to CISA, INTERPOL, and relevant national authorities. All sessions are audited under FedRAMP and DoD security controls.
                </p>
              </div>
            </div>
          </div>

          {/* Legal links */}
          <div className="flex items-center justify-center gap-4 mt-5 text-[10px] text-slate-500">
            <a href="/privacy-policy" className="hover:text-slate-300 transition-colors flex items-center gap-1">
              <Shield className="w-3 h-3" />Privacy Policy
            </a>
            <span>&bull;</span>
            <a href="/user-agreement" className="hover:text-slate-300 transition-colors flex items-center gap-1">
              <ScrollText className="w-3 h-3" />User Agreement
            </a>
            <span>&bull;</span>
            <a href="/documentation" className="hover:text-slate-300 transition-colors flex items-center gap-1">
              <BookOpen className="w-3 h-3" />Documentation
            </a>
          </div>
        </div>
      </div>

      {/* Bottom classification banner */}
      <div className="bg-red-700 text-white text-center py-1.5 text-xs font-bold tracking-[0.25em] uppercase">
        TOP SECRET // AUTHORIZED PERSONNEL ONLY // OEADS ORGANIZATIONAL SYSTEM
      </div>
    </div>
  );
}
