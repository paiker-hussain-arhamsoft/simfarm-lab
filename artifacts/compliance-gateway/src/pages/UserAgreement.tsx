import { Shield, ArrowLeft, AlertTriangle, FileText, ScrollText } from "lucide-react";

const CLAUSES = [
  {
    title: "1. Parties and Scope",
    content: `This User Agreement ("Agreement") is entered into between the authorized organizational operator of the Orchestrated Educational AI Deployment System ("OEADS," "Platform," "we," "us") and you, the authenticated individual user ("User," "you"). This Agreement governs all access to and use of the OEADS platform, including all AI workspaces, data pipelines, agent orchestration systems, and supporting infrastructure. This Agreement is binding upon acceptance of the six-item Compliance Gate and upon each authenticated session.`,
  },
  {
    title: "2. Authorization and Access Controls",
    content: `Access to OEADS is strictly limited to personnel who have been individually authorized by the organizational administrator. You acknowledge that: (a) your organizational credentials (username, password) and portal security key are personal, non-transferable, and must be protected against unauthorized disclosure; (b) sharing credentials constitutes a material breach of this Agreement and may constitute a violation of the Computer Fraud and Abuse Act (18 U.S.C. § 1030); (c) you are responsible for all activity conducted under your authenticated session; (d) portal key unmounting is an affirmative security action — you accept full responsibility for portal key custody; (e) the organizational administrator may revoke access at any time without notice for cause.`,
  },
  {
    title: "3. Permitted Use",
    content: `OEADS tools and AI workspaces are authorized solely for the following purposes: (a) educational research and policy analysis conducted by authorized organizational personnel; (b) authorized security research within explicitly scoped, legally compliant engagements; (c) organizational training and capability development activities; (d) authorized testing and evaluation of AI orchestration methodologies. All use must comply with applicable law including but not limited to the TCPA (47 U.S.C. § 227), CFAA (18 U.S.C. § 1030), FEC regulations (52 U.S.C. § 30101 et seq.), and applicable international law.`,
  },
  {
    title: "4. Prohibited Conduct",
    content: `You expressly agree not to: (a) use OEADS tools for unauthorized computer access, fraud, identity theft, or any unlawful purpose; (b) use IVR, SIM Farm, or proxy tools for unsolicited communications in violation of the TCPA or equivalent laws; (c) use electoral analysis tools to unlawfully influence, suppress, or manipulate elections in violation of FEC regulations; (d) use persona or deepfake tools to impersonate real individuals without explicit written consent; (e) use cyber tools against systems or networks without explicit written authorization from the system owner; (f) use content distribution tools to distribute disinformation, malware, phishing content, or illegal material; (g) circumvent, disable, or interfere with platform security controls; (h) share, resell, or sublicense access to OEADS; (i) use OEADS outputs to train competing AI systems.`,
  },
  {
    title: "5. Compliance with Regulatory Bodies",
    content: `By using OEADS, you agree to comply with applicable directives, guidelines, and obligations issued or enforced by the following authorities:\n\n• FedRAMP — federal cloud security requirements applicable to U.S. government-adjacent operations\n• DoD — Department of Defense security controls, CMMC requirements, and handling procedures for controlled unclassified information\n• CISA (US) — incident reporting obligations for significant cybersecurity events; you agree to support CISA investigations arising from OEADS-related activity\n• NCSC (UK) — responsible vulnerability disclosure obligations; Cyber Essentials compliance for UK-jurisdiction operations\n• FEC — compliance with federal election law; no use of OEADS outputs in connection with campaign finance violations\n• TCPA — mandatory prior express written consent for all automated outreach; no use of IVR or SMS tools for unsolicited communications\n• CFAA — strict prohibition on unauthorized computer access; you accept criminal liability under 18 U.S.C. § 1030 for violations\n• ITU/UN — alignment with ITU cybersecurity norms; you agree not to use OEADS in connection with cyberattacks on critical infrastructure\n• INTERPOL — you acknowledge that misuse of OEADS may result in referral to INTERPOL and triggering of INTERPOL Red Notice processes\n• ENISA/EU — GDPR compliance for any processing involving EU personal data; NIS2 Directive obligations for EU-facing security operations\n• AU Cyber Security Centre (ACSC) — Essential Eight compliance for Australian-jurisdiction operations\n• National CERT/CSIRT — coordinated disclosure obligations; you agree to report any security vulnerabilities discovered through OEADS use`,
  },
  {
    title: "6. Intellectual Property — U.S. Patent Act",
    content: `All aspects of OEADS — including its multi-tier agent orchestration architecture, compliance gate methodology, AI pipeline designs, and UI — are proprietary intellectual property protected under the United States Patent Act (35 U.S.C.) and applicable copyright and trade secret law. No license to copy, reproduce, reverse engineer, or create derivative works is granted by this Agreement. Your right to use OEADS is a limited, non-exclusive, non-transferable, revocable license for the organizational purposes described in Section 3 only.`,
  },
  {
    title: "7. Audit, Monitoring, and Consent to Logging",
    content: `You expressly consent to: (a) complete logging of all authentication events, compliance acknowledgments, page navigation, and AI pipeline activity; (b) administrative review of all logged data by authorized organizational personnel; (c) disclosure of logs to law enforcement, regulatory agencies, and national security authorities pursuant to valid legal process; (d) retention of audit logs for a minimum of 90 days and consent records indefinitely. You have no expectation of privacy with respect to activity conducted on OEADS. All sessions are monitored in compliance with FedRAMP continuous monitoring requirements and DoD audit controls.`,
  },
  {
    title: "8. Disclaimer of Warranties",
    content: `OEADS is provided on an "as-is" and "as-available" basis for authorized organizational use. The platform makes no warranty, express or implied, regarding the accuracy, completeness, or fitness for purpose of AI-generated outputs. AI outputs are research artifacts only and do not constitute legal, medical, financial, or professional advice. Users are solely responsible for evaluating and acting upon AI-generated content.`,
  },
  {
    title: "9. Limitation of Liability",
    content: `To the maximum extent permitted by law, OEADS and its organizational operators shall not be liable for any indirect, incidental, consequential, special, or punitive damages arising from use of the platform. The User assumes full legal responsibility for how OEADS outputs are applied in the real world. The total liability of OEADS for any claim shall not exceed the organizational license fee paid in the twelve months preceding the claim.`,
  },
  {
    title: "10. Termination",
    content: `This Agreement may be terminated immediately by the organizational administrator for cause, including any breach of the prohibited conduct provisions, credential sharing, or suspected unauthorized access. Upon termination, all access rights immediately cease, session tokens are invalidated, and the User must not attempt to re-access the platform. Obligations of confidentiality, IP protection, and regulatory compliance survive termination.`,
  },
  {
    title: "11. Governing Law and Jurisdiction",
    content: `This Agreement is governed by the laws of the United States. Disputes arising under this Agreement shall be subject to the exclusive jurisdiction of the federal courts of the United States. For EU-based users, mandatory consumer protection provisions of the applicable EU member state law apply to the extent required by law. Nothing in this Agreement limits any rights or obligations arising under applicable criminal law, including the CFAA, or international law.`,
  },
  {
    title: "12. Acceptance",
    content: `By authenticating to OEADS and acknowledging the six-item Compliance Gate, you confirm that you: (a) are an authorized organizational user; (b) have read and understood this Agreement in its entirety; (c) agree to be bound by all terms and conditions; (d) have the legal capacity and organizational authorization to enter this Agreement; (e) accept all compliance obligations to the regulatory bodies named herein.`,
  },
];

export default function UserAgreement() {
  return (
    <div className="min-h-screen bg-[#080c14] flex flex-col">
      <div className="bg-red-700 text-white text-center py-1.5 text-xs font-bold tracking-[0.25em] uppercase">
        TOP SECRET // AUTHORIZED PERSONNEL ONLY // OEADS ORGANIZATIONAL SYSTEM
      </div>

      <div className="max-w-3xl mx-auto w-full px-4 py-10 flex-1">
        <a href="/login" className="flex items-center gap-1.5 text-slate-500 hover:text-slate-300 text-xs mb-8 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />Back to Login
        </a>

        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-violet-600/20 border border-violet-500/30 flex items-center justify-center">
              <ScrollText className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <h1 className="text-white text-xl font-bold tracking-wide">User Agreement</h1>
              <p className="text-slate-500 text-xs tracking-wider">OEADS Organizational Platform — Binding Legal Agreement</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-3">
            {["FedRAMP", "DoD", "CISA", "NCSC", "FEC", "TCPA", "CFAA", "ITU", "INTERPOL", "ENISA", "ACSC", "CERT", "GRC", "Patent Act"].map((a) => (
              <span key={a} className="px-2 py-0.5 rounded text-[9px] font-bold tracking-widest uppercase border border-slate-700/50 bg-slate-800/60 text-slate-400">
                {a}
              </span>
            ))}
          </div>
          <div className="mt-4 p-3 rounded-lg bg-amber-950/20 border border-amber-700/30 flex items-start gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 mt-0.5 flex-shrink-0" />
            <p className="text-[10px] text-amber-300/80 leading-relaxed">
              This is a legally binding agreement. By authenticating to OEADS and completing the Compliance Gate, you confirm full acceptance of all terms. Unauthorized access or misuse may result in criminal prosecution under the CFAA, TCPA, and applicable international law.
            </p>
          </div>
          <div className="flex gap-2 mt-3">
            <span className="px-2 py-0.5 rounded bg-red-900/60 border border-red-700/50 text-red-300 text-[9px] font-bold tracking-widest uppercase">Confidential</span>
            <span className="px-2 py-0.5 rounded bg-orange-900/60 border border-orange-700/50 text-orange-300 text-[9px] font-bold tracking-widest uppercase">Top Secret</span>
            <span className="px-2 py-0.5 rounded bg-violet-900/60 border border-violet-700/50 text-violet-300 text-[9px] font-bold tracking-widest uppercase">GRC Compliant</span>
          </div>
        </div>

        <div className="space-y-6">
          {CLAUSES.map((c, i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-6">
              <h2 className="text-slate-200 font-semibold text-sm mb-3 flex items-center gap-2">
                <FileText className="w-3.5 h-3.5 text-violet-400" />
                {c.title}
              </h2>
              <div className="text-slate-400 text-xs leading-relaxed whitespace-pre-line">{c.content}</div>
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
