import { ArrowLeft, BookOpen, Cpu, Shield, Lock, Database, Layers, AlertTriangle, FileText, Globe, Usb, KeyRound } from "lucide-react";

const TIERS = [
  {
    tier: "TIER 1",
    name: "Strategic Brain",
    route: "/tool",
    color: "text-blue-400",
    border: "border-blue-700/30",
    bg: "bg-blue-950/10",
    agents: ["Researcher", "Synthesizer", "Critic", "Director"],
    description: "General-purpose multi-agent research and strategic analysis pipeline. Four sequential AI agents produce a complete research report from a given topic.",
    api: "POST /api/agents/plan",
  },
  {
    tier: "TIER 2A",
    name: "Intelligence Crew",
    route: "/tier2",
    color: "text-violet-400",
    border: "border-violet-700/30",
    bg: "bg-violet-950/10",
    agents: ["Intelligence Lead", "Behavior Forecaster", "Social Media Strategist", "Synthesizer"],
    description: "Voter behavior profiling, demographic intelligence, and social platform targeting analysis. For authorized political research and policy analysis.",
    api: "POST /api/intelligence/plan",
  },
  {
    tier: "TIER 2B",
    name: "Media Crew",
    route: "/media-crew",
    color: "text-orange-400",
    border: "border-orange-700/30",
    bg: "bg-orange-950/10",
    agents: ["Face Architect", "Voice Architect", "Lip Sync Engineer", "Production Lead"],
    description: "Digital human avatar production pipeline. HeyGen, ElevenLabs, Wav2Lip, and SadTalker integration for educational synthetic media research.",
    api: "POST /api/media/plan",
  },
  {
    tier: "TIER 2C",
    name: "Video Deepfake Stack",
    route: "/video-stack",
    color: "text-cyan-400",
    border: "border-cyan-700/30",
    bg: "bg-cyan-950/10",
    agents: ["Render Strategist", "Script Writer", "Technical Director", "Video Director"],
    description: "DeepFaceLab, FaceSwap, GFPGAN, and FFMPEG pipeline design. Authorized research into synthetic video generation and detection methodologies.",
    api: "POST /api/video/plan",
  },
  {
    tier: "TIER 2D",
    name: "Cyber Crew",
    route: "/cyber-crew",
    color: "text-red-400",
    border: "border-red-700/30",
    bg: "bg-red-950/10",
    agents: ["Red Team Strategist", "DAST Engineer", "TLS Fingerprint Engineer", "Security Director"],
    description: "Authorized penetration testing methodology design. Nmap, OpenVAS, Metasploit, OWASP ZAP orchestration for scoped security assessments.",
    api: "POST /api/cyber/plan",
  },
  {
    tier: "TIER 3",
    name: "Persona Orchestration",
    route: "/persona-orchestration",
    color: "text-purple-400",
    border: "border-purple-700/30",
    bg: "bg-purple-950/10",
    agents: ["Persona Architect", "Behavior Architect", "Dialect Specialist", "Orchestration Engineer"],
    description: "Synthetic identity design and fleet management for authorized research. Behavioral modeling, voice calibration, and lifecycle orchestration.",
    api: "POST /api/persona/plan",
  },
  {
    tier: "TIER 4A",
    name: "SIM Farm",
    route: "/sim-farm",
    color: "text-green-400",
    border: "border-green-700/30",
    bg: "bg-green-950/10",
    agents: ["Hardware Architect", "SMSGate Engineer", "SIM Farm Strategist", "Automation Director"],
    description: "SIM800/SIM900 hardware topology, SMSGate gateway configuration, number provisioning, and Celery campaign automation design.",
    api: "POST /api/sim/plan",
  },
  {
    tier: "TIER 4B",
    name: "Proxy Rotation",
    route: "/proxy-rotation",
    color: "text-blue-400",
    border: "border-blue-700/30",
    bg: "bg-blue-950/10",
    agents: ["Infrastructure Architect", "Proxy Pool Engineer", "Integration Strategist", "Operations Director"],
    description: "Scrapoxy-based proxy pool infrastructure design, Playwright/Puppeteer integration, health monitoring, and rotation algorithm specification.",
    api: "POST /api/proxy/plan",
  },
  {
    tier: "TIER 4C",
    name: "IVR Systems",
    route: "/ivr-systems",
    color: "text-orange-400",
    border: "border-orange-700/30",
    bg: "bg-orange-950/10",
    agents: ["IVR Hardware Architect", "Call Flow Engineer", "Rural Penetration Strategist", "Operations Director"],
    description: "Raspberry Pi + GSM modem IVR hardware, Verboice/VBVoice call tree design, and rural low-bandwidth targeting methodology.",
    api: "POST /api/ivr/plan",
  },
  {
    tier: "TIER 4D",
    name: "Content Distribution",
    route: "/content-distribution",
    color: "text-green-400",
    border: "border-green-700/30",
    bg: "bg-green-950/10",
    agents: ["Marketing Automation Architect", "CMS Engineer", "Social Media Manager", "Operations Director"],
    description: "Mautic drip campaign, Strapi AI-CMS, Postiz social scheduler, and satellite site webhook chain — the complete Blogger Machine.",
    api: "POST /api/content/plan",
  },
  {
    tier: "TIER 4E",
    name: "Stealth & Anti-Detection",
    route: "/stealth-detection",
    color: "text-orange-400",
    border: "border-orange-700/30",
    bg: "bg-orange-950/10",
    agents: ["Stealth Browser Architect", "Cloudflare Bypass Engineer", "Browser Infrastructure Strategist", "Operations Director"],
    description: "playwright-extra evasion, FlareSolverr Cloudflare bypass, Browserbase/Scrapoxy fingerprint pool design, and 12-signal evasion matrix.",
    api: "POST /api/stealth/plan",
  },
  {
    tier: "TIER 4F",
    name: "Memory & Persistence",
    route: "/memory-persistence",
    color: "text-indigo-400",
    border: "border-indigo-700/30",
    bg: "bg-indigo-950/10",
    agents: ["Mem0 Memory Architect", "Zeta Memory Engineer", "Data Lake Architect", "Operations Director"],
    description: "Mem0+Qdrant+Neo4j memory graph, PostgreSQL+pgvector hot/warm/cold tiering, Kafka+Cassandra 120M-record data lake, and OEADS integration guide.",
    api: "POST /api/memory/plan",
  },
];

export default function Documentation() {
  return (
    <div className="min-h-screen bg-[#080c14] flex flex-col">
      <div className="bg-red-700 text-white text-center py-1.5 text-xs font-bold tracking-[0.25em] uppercase">
        TOP SECRET // AUTHORIZED PERSONNEL ONLY // OEADS ORGANIZATIONAL SYSTEM
      </div>

      <div className="max-w-4xl mx-auto w-full px-4 py-10 flex-1">
        <a href="/login" className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 text-xs mb-8 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />Back to Login
        </a>

        {/* Header */}
        <div className="mb-10">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h1 className="text-white text-xl font-bold tracking-wide">Technical Documentation</h1>
              <p className="text-slate-500 text-xs tracking-wider">OEADS — Orchestrated Educational AI Deployment System</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-3">
            {["FedRAMP", "DoD", "CISA", "NCSC", "FEC", "TCPA", "CFAA", "ITU", "INTERPOL", "ENISA", "ACSC", "CERT", "GRC"].map((a) => (
              <span key={a} className="px-2 py-0.5 rounded text-[9px] font-bold tracking-widest uppercase border border-slate-700/50 bg-slate-800/60 text-slate-400">
                {a}
              </span>
            ))}
          </div>
          <div className="flex gap-2 mt-3">
            <span className="px-2 py-0.5 rounded bg-red-900/60 border border-red-700/50 text-red-300 text-[9px] font-bold tracking-widest uppercase">Confidential</span>
            <span className="px-2 py-0.5 rounded bg-orange-900/60 border border-orange-700/50 text-orange-300 text-[9px] font-bold tracking-widest uppercase">Top Secret</span>
            <span className="px-2 py-0.5 rounded bg-green-900/60 border border-green-700/50 text-green-300 text-[9px] font-bold tracking-widest uppercase">Secure Site</span>
            <span className="px-2 py-0.5 rounded bg-violet-900/60 border border-violet-700/50 text-violet-300 text-[9px] font-bold tracking-widest uppercase">GRC Compliant</span>
          </div>
        </div>

        {/* Auth Architecture */}
        <section className="mb-10">
          <h2 className="text-slate-200 font-semibold text-sm mb-4 flex items-center gap-2">
            <Lock className="w-4 h-4 text-blue-400" />
            Authentication Architecture
          </h2>
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-6 space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800/60 rounded-lg p-4 border border-slate-700/40">
                <div className="text-[10px] font-bold text-blue-400 tracking-widest uppercase mb-2">Factor 1</div>
                <div className="text-slate-200 text-xs font-semibold mb-1">Organizational Username</div>
                <div className="text-slate-500 text-[10px]">Unique organizational identifier. Validated server-side against AUTH_USERNAME environment variable.</div>
              </div>
              <div className="bg-slate-800/60 rounded-lg p-4 border border-slate-700/40">
                <div className="text-[10px] font-bold text-violet-400 tracking-widest uppercase mb-2">Factor 2</div>
                <div className="text-slate-200 text-xs font-semibold mb-1">Password (SHA-256)</div>
                <div className="text-slate-500 text-[10px]">Password is SHA-256 hashed in the browser before transmission. Plaintext never leaves the client. Server compares hash against stored hash of AUTH_PASSWORD.</div>
              </div>
              <div className="bg-slate-800/60 rounded-lg p-4 border border-slate-700/40">
                <div className="text-[10px] font-bold text-orange-400 tracking-widest uppercase mb-2">Factor 3</div>
                <div className="text-slate-200 text-xs font-semibold mb-1">Portal Security Key</div>
                <div className="text-slate-500 text-[10px]">SHA-256 hash of the portal key is stored in browser localStorage. The stored hash is sent to the server for validation — plaintext key never transmitted.</div>
              </div>
            </div>
            <div className="bg-slate-800/40 rounded-lg p-4 border border-slate-700/30">
              <div className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-2">Portal Key Lifecycle</div>
              <div className="text-slate-400 text-xs leading-relaxed space-y-1">
                <div><span className="text-green-400 font-semibold">Mount:</span> User enters raw portal key &rarr; browser computes SHA-256 &rarr; hash stored in localStorage as <code className="text-slate-300">oeads_portal_key</code></div>
                <div><span className="text-orange-400 font-semibold">Unmount:</span> localStorage entry removed + session token cleared &rarr; full re-authentication required</div>
                <div><span className="text-blue-400 font-semibold">Session token:</span> 256-bit cryptographically random token issued by server on successful login &rarr; stored in sessionStorage as <code className="text-slate-300">oeads_auth_token</code></div>
                <div><span className="text-red-400 font-semibold">Protection:</span> All workspace routes check both sessionStorage token AND localStorage portal key hash on mount — missing either redirects to /login</div>
              </div>
            </div>
          </div>
        </section>

        {/* System Architecture */}
        <section className="mb-10">
          <h2 className="text-slate-200 font-semibold text-sm mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            System Architecture
          </h2>
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <div className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-2">Frontend</div>
                <div className="text-xs text-slate-400 space-y-0.5 leading-relaxed">
                  <div>React 19 + Vite (TypeScript)</div>
                  <div>Wouter client-side routing</div>
                  <div>TanStack Query v5</div>
                  <div>Radix UI primitives</div>
                  <div>Tailwind CSS v4</div>
                  <div>Lucide React icons</div>
                </div>
              </div>
              <div>
                <div className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-2">Backend</div>
                <div className="text-xs text-slate-400 space-y-0.5 leading-relaxed">
                  <div>Express 5 + Node.js ESM</div>
                  <div>esbuild bundle pipeline</div>
                  <div>Pino structured logging</div>
                  <div>Drizzle ORM + PostgreSQL</div>
                  <div>OpenAI gpt-5.2 (SSE streaming)</div>
                  <div>Replit AI Integrations proxy</div>
                </div>
              </div>
            </div>
            <div className="border-t border-slate-700/40 pt-4">
              <div className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-2">Data Flow</div>
              <div className="text-xs text-slate-500 font-mono leading-relaxed">
                Browser &rarr; Compliance Gate (/) &rarr; Access Granted (/access) &rarr; Workspace (/tool | /tier2 | ...) &rarr; POST /api/*/plan &rarr; OpenAI SSE stream &rarr; 4-agent pipeline &rarr; UI render
              </div>
            </div>
          </div>
        </section>

        {/* SSE Protocol */}
        <section className="mb-10">
          <h2 className="text-slate-200 font-semibold text-sm mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            AI Pipeline — SSE Event Protocol
          </h2>
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-6">
            <div className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-3">Server-Sent Event Types</div>
            <div className="space-y-2 font-mono text-xs">
              {[
                { type: "agent_start", color: "text-blue-400", desc: "Agent begins — carries role, tool, color metadata" },
                { type: "token", color: "text-green-400", desc: "Streaming token chunk from the active agent" },
                { type: "agent_done", color: "text-violet-400", desc: "Agent has finished producing its full response" },
                { type: "done", color: "text-orange-400", desc: "All agents complete — pipeline finished" },
                { type: "error", color: "text-red-400", desc: "Pipeline error — message field contains details" },
              ].map((e) => (
                <div key={e.type} className="flex items-start gap-3">
                  <span className={`${e.color} font-bold w-24 flex-shrink-0`}>{e.type}</span>
                  <span className="text-slate-500">{e.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Regulatory Compliance Section */}
        <section className="mb-10">
          <h2 className="text-slate-200 font-semibold text-sm mb-4 flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-400" />
            Regulatory Approvals & Compliance Framework
          </h2>
          <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-6">
            <div className="text-[10px] font-bold text-slate-400 tracking-widest uppercase mb-4">Governing Bodies</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                { name: "FedRAMP", desc: "Federal Risk & Authorization Management Program — cloud security continuous monitoring" },
                { name: "DoD / CMMC", desc: "Department of Defense — CMMC Level 3, NIST SP 800-171 controlled unclassified information" },
                { name: "CISA (US)", desc: "Cybersecurity & Infrastructure Security Agency — incident reporting, threat intel" },
                { name: "NCSC (UK)", desc: "National Cyber Security Centre — Cyber Essentials Plus, responsible AI/security research" },
                { name: "FEC", desc: "Federal Election Commission — lawful electoral data use, campaign finance compliance" },
                { name: "TCPA", desc: "Telephone Consumer Protection Act — prior express written consent for all automated comms" },
                { name: "CFAA", desc: "Computer Fraud & Abuse Act — authorized access only; violations carry criminal liability" },
                { name: "ITU / UN", desc: "International Telecommunication Union — ICT security norms, telecom regulatory alignment" },
                { name: "INTERPOL", desc: "International Criminal Police Organization — law enforcement data sharing obligations" },
                { name: "ENISA / EU", desc: "EU Agency for Cybersecurity — GDPR, NIS2 Directive, EU data protection standards" },
                { name: "ACSC (AU)", desc: "Australian Cyber Security Centre — Essential Eight maturity model" },
                { name: "CERT/CSIRT", desc: "National CERT/CSIRT Network — coordinated disclosure and incident response obligations" },
                { name: "U.S. Patent Act", desc: "35 U.S.C. — OEADS IP and methodology protected; unauthorized reproduction prohibited" },
                { name: "GRC Framework", desc: "Integrated Governance, Risk & Compliance posture across all tiers and operations" },
              ].map((r) => (
                <div key={r.name} className="bg-slate-800/40 rounded-lg p-3 border border-slate-700/30">
                  <div className="text-slate-300 text-[10px] font-bold tracking-widest uppercase mb-1">{r.name}</div>
                  <div className="text-slate-500 text-[10px] leading-relaxed">{r.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Workspace Reference */}
        <section className="mb-10">
          <h2 className="text-slate-200 font-semibold text-sm mb-4 flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            Workspace Reference
          </h2>
          <div className="space-y-3">
            {TIERS.map((t) => (
              <div key={t.tier} className={`rounded-xl border p-4 ${t.border} ${t.bg}`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-[9px] font-bold tracking-widest uppercase ${t.color}`}>{t.tier}</span>
                      <span className="text-slate-200 text-xs font-semibold">{t.name}</span>
                      <span className="text-slate-600 text-[9px] font-mono">{t.route}</span>
                    </div>
                    <p className="text-slate-500 text-[10px] leading-relaxed mb-2">{t.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {t.agents.map((a) => (
                        <span key={a} className="px-1.5 py-0.5 rounded text-[9px] bg-slate-800/80 border border-slate-700/40 text-slate-400">{a}</span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <code className={`text-[9px] font-mono ${t.color}`}>{t.api}</code>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="mt-8 text-center text-[10px] text-slate-600">
          Protected under the U.S. Patent Act (35 U.S.C.) &bull; OEADS &copy; {new Date().getFullYear()} &bull; All rights reserved
        </div>
      </div>

      <div className="bg-red-700 text-white text-center py-1.5 text-xs font-bold tracking-[0.25em] uppercase">
        TOP SECRET // AUTHORIZED PERSONNEL ONLY // OEADS ORGANIZATIONAL SYSTEM
      </div>
    </div>
  );
}
