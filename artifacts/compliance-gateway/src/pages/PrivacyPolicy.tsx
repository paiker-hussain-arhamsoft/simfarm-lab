import { Shield, ArrowLeft, Lock, Eye, Database, Globe, AlertTriangle, FileText } from "lucide-react";

const SECTIONS = [
  {
    id: "overview",
    title: "1. Overview and Scope",
    content: `This Privacy Policy governs the collection, processing, storage, and disclosure of information by the Orchestrated Educational AI Deployment System (OEADS), an organizational intelligence research platform operated exclusively by authorized personnel. OEADS is designed and operated in compliance with applicable domestic and international legal frameworks governing cybersecurity, data protection, telecommunications, and national security. This policy applies to all authorized users of the platform and all data processed within the OEADS environment.`,
  },
  {
    id: "data-collected",
    title: "2. Data Collected",
    content: `OEADS collects the following categories of data from authenticated users: (a) Session identifiers — unique tokens generated per authenticated session for audit trail purposes; (b) Consent records — immutable records of compliance acknowledgment including timestamp, session ID, and acknowledged items; (c) Activity logs — page navigation events, AI pipeline invocations, query text, configuration selections, and timestamps; (d) Authentication events — login timestamps, authentication outcomes (success/failure), and portal key mount/unmount events; (e) AI pipeline inputs and outputs — research prompts, configuration parameters, and AI-generated responses. No personally identifiable information beyond organizational credentials is solicited or stored by the platform.`,
  },
  {
    id: "legal-basis",
    title: "3. Legal Basis for Processing",
    content: `Data processing within OEADS is conducted on the following legal bases: (a) Legitimate organizational interest — operational security monitoring, compliance auditing, and authorized research activities; (b) Contractual obligation — users are bound by the OEADS User Agreement which establishes the legal basis for processing; (c) Legal obligation — audit and logging requirements under FedRAMP, DoD security controls (NIST SP 800-53), and applicable national CERT/CSIRT requirements; (d) Consent — users explicitly acknowledge and consent to data processing through the compliance gate before accessing any platform functionality.`,
  },
  {
    id: "regulatory",
    title: "4. Regulatory Compliance Framework",
    content: `OEADS operates under a comprehensive governance, risk, and compliance (GRC) framework aligned with the following regulatory bodies and legal instruments:\n\n• FedRAMP (Federal Risk and Authorization Management Program) — cloud security controls and continuous monitoring requirements\n• DoD (U.S. Department of Defense) — CMMC Level 3 alignment, NIST SP 800-171 data protection requirements\n• CISA (Cybersecurity and Infrastructure Security Agency, US) — threat intelligence sharing protocols, incident reporting obligations\n• NCSC (National Cyber Security Centre, UK) — Cyber Essentials Plus alignment, responsible use of AI in security contexts\n• FEC (Federal Election Commission) — lawful use restrictions for electoral data and voter behavior analysis tools\n• TCPA (Telephone Consumer Protection Act, 47 U.S.C. § 227) — lawful use requirements for IVR, SMS, and automated dialing tools\n• CFAA (Computer Fraud and Abuse Act, 18 U.S.C. § 1030) — unauthorized access prohibitions and computer fraud controls\n• ITU (International Telecommunication Union, UN) — ICT security norms, cybersecurity guidelines, and telecom regulatory alignment\n• INTERPOL (International Criminal Police Organization) — law enforcement data sharing obligations; unauthorized use may trigger INTERPOL notice processes\n• ENISA (European Union Agency for Cybersecurity) — GDPR-adjacent controls, NIS2 Directive alignment for EU-facing operations\n• AU Cyber Security Centre (ACSC) — Essential Eight maturity model alignment for Australian-jurisdiction operations\n• National CERT/CSIRT Network — coordinated vulnerability disclosure and incident response obligations\n• GRC Framework — integrated governance, risk management, and compliance posture across all tiers`,
  },
  {
    id: "patent",
    title: "5. Intellectual Property — U.S. Patent Act",
    content: `OEADS and its constituent methodologies, orchestration architectures, and AI pipeline designs are protected under the United States Patent Act (35 U.S.C.). All intellectual property embodied in the OEADS platform, including but not limited to its multi-tier agent orchestration methodology, compliance gate architecture, and AI pipeline designs, constitutes proprietary organizational IP. Unauthorized reproduction, reverse engineering, or commercial exploitation is strictly prohibited and constitutes grounds for legal action under applicable IP law.`,
  },
  {
    id: "data-retention",
    title: "6. Data Retention and Deletion",
    content: `Session data and activity logs are retained for a minimum of 90 days for audit compliance purposes. Consent records are retained indefinitely as an immutable audit trail. AI pipeline outputs are not retained server-side beyond the active session. Users may request deletion of their session data subject to applicable legal hold obligations. Requests for data deletion must be submitted through the authorized organizational channel and will be processed within 30 days, subject to mandatory retention requirements under applicable law.`,
  },
  {
    id: "security",
    title: "7. Security Controls",
    content: `OEADS implements the following security controls: (a) Three-factor authentication — organizational username, password (SHA-256 hashed in transit), and browser-resident portal security key; (b) Session tokens — cryptographically random 256-bit tokens with session-scope validity; (c) Portal key hashing — SHA-256 hash of the portal key is stored in browser localStorage; the plaintext key is never transmitted; (d) Compliance gate — six-item mandatory acknowledgment requirement before any tool access; (e) Session isolation — each browser session is independently authenticated; (f) Audit logging — all events are logged to an append-only audit table in the organizational database; (g) Admin oversight — authorized administrators can review all session and activity data.`,
  },
  {
    id: "third-party",
    title: "8. Third-Party Data Sharing",
    content: `OEADS does not sell, rent, or commercially share user data with third parties. Data may be disclosed in the following circumstances: (a) Legal obligation — in response to valid legal process from a court, law enforcement agency, or regulatory authority with jurisdiction; (b) National security — pursuant to national security letters, FISA orders, or equivalent instruments; (c) INTERPOL cooperation — in connection with international law enforcement data sharing obligations; (d) Incident response — to national CERT/CSIRT teams in the event of a confirmed security incident; (e) Organizational governance — to authorized internal administrators and oversight personnel. All AI query traffic is routed through OpenAI's API under OpenAI's enterprise data processing agreements and subject to OpenAI's privacy policy.`,
  },
  {
    id: "user-rights",
    title: "9. User Rights",
    content: `Authorized users have the following rights subject to applicable law: the right to access their session and activity data through the admin panel; the right to request correction of inaccurate data; the right to request deletion subject to legal retention requirements; the right to lodge a complaint with the applicable supervisory authority (e.g., ENISA for EU users, ICO for UK users, OAIC for Australian users). These rights may be limited by national security, law enforcement, and audit obligations.`,
  },
  {
    id: "contact",
    title: "10. Contact and Updates",
    content: `This Privacy Policy is reviewed and updated as required by changes in applicable law or organizational policy. Continued use of OEADS following any material update constitutes acceptance of the revised policy. For privacy-related inquiries, contact the organizational data protection officer through the authorized internal channel. This policy is effective as of the OEADS platform deployment date and supersedes all prior privacy statements.`,
  },
];

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-[#080c14] flex flex-col">
      <div className="bg-red-700 text-white text-center py-1.5 text-xs font-bold tracking-[0.25em] uppercase">
        TOP SECRET // AUTHORIZED PERSONNEL ONLY // OEADS ORGANIZATIONAL SYSTEM
      </div>

      <div className="max-w-3xl mx-auto w-full px-4 py-10 flex-1">
        {/* Back */}
        <a href="/login" className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 text-xs mb-8 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />Back to Login
        </a>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
              <Shield className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h1 className="text-white text-xl font-bold tracking-wide">Privacy Policy</h1>
              <p className="text-slate-500 text-xs tracking-wider">OEADS Organizational Platform</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-3">
            {["FedRAMP", "DoD", "CISA", "NCSC", "FEC", "TCPA", "CFAA", "ITU", "INTERPOL", "ENISA", "ACSC", "CERT", "GRC"].map((a) => (
              <span key={a} className="px-2 py-0.5 rounded text-[9px] font-bold tracking-widest uppercase border border-slate-700/50 bg-slate-800/60 text-slate-400">
                {a}
              </span>
            ))}
          </div>
          <div className="mt-4 p-3 rounded-lg bg-amber-950/20 border border-amber-700/30 flex items-start gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 mt-0.5 flex-shrink-0" />
            <p className="text-[10px] text-amber-300/80 leading-relaxed">
              This document is classified CONFIDENTIAL. Distribution is restricted to authorized OEADS personnel. Unauthorized disclosure is prohibited under the CFAA (18 U.S.C. § 1030) and applicable national security law.
            </p>
          </div>
          <div className="flex gap-2 mt-3">
            <span className="px-2 py-0.5 rounded bg-red-900/60 border border-red-700/50 text-red-300 text-[9px] font-bold tracking-widest uppercase">Confidential</span>
            <span className="px-2 py-0.5 rounded bg-orange-900/60 border border-orange-700/50 text-orange-300 text-[9px] font-bold tracking-widest uppercase">Top Secret</span>
            <span className="px-2 py-0.5 rounded bg-green-900/60 border border-green-700/50 text-green-300 text-[9px] font-bold tracking-widest uppercase">Secure Site</span>
            <span className="px-2 py-0.5 rounded bg-violet-900/60 border border-violet-700/50 text-violet-300 text-[9px] font-bold tracking-widest uppercase">GRC Compliant</span>
          </div>
        </div>

        {/* Sections */}
        <div className="space-y-6">
          {SECTIONS.map((s) => (
            <div key={s.id} className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-6">
              <h2 className="text-slate-200 font-semibold text-sm mb-3 flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-blue-400" />
                {s.title}
              </h2>
              <div className="text-slate-400 text-xs leading-relaxed whitespace-pre-line">{s.content}</div>
            </div>
          ))}
        </div>

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
