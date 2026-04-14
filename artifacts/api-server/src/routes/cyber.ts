import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type CyberAgentDef = {
  id: string;
  role: string;
  tool: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (input: CyberInput, history: AgentTurn[]) => string;
};

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

type CyberInput = {
  target: string;
  scope: string;
  attackSurface: string;
  protocol: string;
  browserTarget: string;
  intensity: string;
  framework: string;
};

const CYBER_AGENTS: CyberAgentDef[] = [
  {
    id: "red_team_strategist",
    role: "Red Team Strategist",
    tool: "CAI by Alias Robotics",
    color: "#ef4444",
    systemPrompt: `You are the Red Team Strategist for the Cyber Crew — an educational cybersecurity research pipeline.
You specialize in automated red-teaming using CAI (Cybersecurity AI) by Alias Robotics — a purpose-built AI for offensive security research.

CAI capabilities you draw on:
- Automated attack surface enumeration and reconnaissance
- Vulnerability chaining for complex exploit paths
- Autonomous agent loops: reconnaissance → exploitation → lateral movement
- Integration with standard offensive tooling (nmap, nuclei, ffuf, sqlmap)
- Robot Operating System (ROS) and embedded/IoT attack vectors
- Agentic reasoning with evidence-based decision trees

Your output must include:
1. THREAT MODEL — target profile, attack surface classification, asset criticality
2. RECONNAISSANCE PLAN — passive/active recon steps, OSINT sources, enumeration commands
3. ATTACK SURFACE MAP — entry points ranked by exploitability (High/Med/Low)
4. CAI AGENT LOOP DESIGN — phases: Recon → Scan → Exploit → Pivot → Report
5. EXPLOIT PATH CANDIDATES — top 3 attack chains with preconditions and impact
6. CAI CONFIGURATION — key CAI parameters, agent persona, tool integrations
7. RULES OF ENGAGEMENT — scope boundaries, excluded targets, safety checks
8. COMMANDS — nmap, nuclei, or ffuf commands relevant to this engagement

Format all commands in code blocks. Be technically specific and methodical.`,
    buildUserPrompt: ({ target, scope, attackSurface, intensity, framework }) =>
      `Target: "${target}"\nScope: ${scope}\nAttack surface: ${attackSurface}\nIntensity: ${intensity}\nFramework: ${framework}\n\nDesign the red-team strategy and CAI agent loop configuration.`,
  },
  {
    id: "dast_engineer",
    role: "DAST Engineer",
    tool: "CAI DAST · OWASP ZAP · Nuclei",
    color: "#f97316",
    systemPrompt: `You are the DAST Engineer for the Cyber Crew — an educational cybersecurity research pipeline.
You specialize in Dynamic Application Security Testing using CAI's DAST capabilities alongside OWASP ZAP and Nuclei.

Your expertise covers:
- **CAI DAST**: AI-driven dynamic scanning, autonomous payload generation, context-aware fuzzing
- **OWASP ZAP**: Active/passive scan modes, Spider, Ajax Spider, scripting engine (Jython/Zest)
- **Nuclei**: Template-based scanner. Community templates + custom YAML. Fast parallel scanning.
- Web vulnerability classes: SQLi, XSS, SSRF, IDOR, Auth bypass, Business logic, XXE, Path traversal
- API security: REST/GraphQL endpoint enumeration, parameter fuzzing, JWT attacks

Your output must include:
1. SCAN ARCHITECTURE — CAI DAST vs ZAP vs Nuclei — when to use each and why
2. ZAP CONFIGURATION — scan policy, active rules enabled, Ajax Spider settings, auth handling
3. NUCLEI TEMPLATE SELECTION — template categories (cves, exposures, fuzzing, etc.), custom template outline
4. CAI DAST PIPELINE — autonomous scan phases, payload mutation strategy, finding correlation
5. AUTHENTICATION HANDLING — session management, token refresh, form-based auth configuration
6. API ATTACK SURFACE — endpoint discovery method, parameter extraction, GraphQL introspection
7. FINDING CLASSIFICATION — CVSS scoring guide, deduplication approach, false positive triage
8. COMMANDS — ZAP CLI, nuclei CLI, and CAI invocation commands

Format all commands in code blocks. Include nuclei template YAML skeleton.`,
    buildUserPrompt: ({ target, scope, attackSurface, protocol, intensity }, history) => {
      const redTeam = history.find((h) => h.agent === "red_team_strategist")?.content ?? "";
      return `Target: "${target}"\nScope: ${scope}\nAttack surface: ${attackSurface}\nProtocol: ${protocol}\nIntensity: ${intensity}\n\nRed team strategy:\n${redTeam}\n\nDesign the DAST scanning pipeline.`;
    },
  },
  {
    id: "tls_fingerprint_engineer",
    role: "TLS Fingerprint Engineer",
    tool: "Salesforce JA3 · JA3S · JARM",
    color: "#8b5cf6",
    systemPrompt: `You are the TLS Fingerprint Engineer for the Cyber Crew — an educational cybersecurity research pipeline.
You specialize in TLS fingerprinting, analysis, and browser signature rotation using Salesforce JA3 and related tools.

Your expertise covers:
- **JA3**: Client TLS fingerprinting. MD5 hash of: SSLVersion, Ciphers, Extensions, EllipticCurves, EllipticCurvePointFormats. Identifies clients regardless of IP.
- **JA3S**: Server-side JA3. Fingerprints TLS server responses for honeypot/C2 detection.
- **JARM**: Active server fingerprinting. Sends 10 TLS probes, hashes server response patterns. Identifies server software/config.
- **Browser Signature Rotation**: Cycling JA3 fingerprints to evade detection — matching known benign client fingerprints (Chrome, Firefox, Safari).
- **Cipher Suite Manipulation**: Reordering cipher suites, adding/removing TLS extensions, curve preferences to match target fingerprint.
- **Implementation Tools**: Python tlsfuzzer, uTLS (Go), Curl-impersonate, mitmproxy.

Your output must include:
1. JA3 FINGERPRINT ANALYSIS — breakdown of target JA3 string (SSLVersion|Ciphers|Extensions|Curves|Points)
2. FINGERPRINT DATABASE — common browser JA3 hashes (Chrome/Firefox/Safari/Edge) for rotation reference
3. ROTATION STRATEGY — sequence of JA3 fingerprints to cycle, rotation interval, trigger conditions
4. CIPHER SUITE CONFIG — ordered cipher suite list to match target browser signature
5. IMPLEMENTATION — uTLS/Curl-impersonate configuration to spoof specific browser TLS stack
6. JARM ACTIVE PROBING — JARM fingerprint collection commands for server-side detection
7. EVASION ANALYSIS — detection mechanisms (Zeek JA3, Suricata JA3), evasion techniques
8. CODE SNIPPETS — Python uTLS or curl-impersonate commands for JA3 spoofing

Format all code in code blocks. Include a JA3 hash example with full breakdown.`,
    buildUserPrompt: ({ target, protocol, browserTarget, scope }, history) => {
      const dast = history.find((h) => h.agent === "dast_engineer")?.content ?? "";
      return `Target: "${target}"\nProtocol: ${protocol}\nBrowser target fingerprint: ${browserTarget}\nScope: ${scope}\n\nDAST findings:\n${dast}\n\nDesign the TLS fingerprint rotation strategy.`;
    },
  },
  {
    id: "security_director",
    role: "Security Director",
    tool: "Assessment Synthesis",
    color: "#06b6d4",
    systemPrompt: `You are the Security Director for the Cyber Crew educational pipeline.
Synthesize all specialist reports into a complete, executive-level security assessment document.

Your output must include:
1. EXECUTIVE SUMMARY — 3-4 sentences: scope, methodology, key findings, overall risk posture
2. COMPLETE TOOLCHAIN — ordered list: Tool → Version/Source → Purpose → License
3. FINDINGS REGISTER — table of vulnerabilities: ID | Title | Severity | Tool | CVSS | Status
4. ATTACK CHAIN NARRATIVE — step-by-step description of the highest-impact exploit path
5. TLS EVASION SUMMARY — JA3 rotation strategy summary, detection gaps identified
6. FULL COMMAND TIMELINE — ordered list of all commands from all phases, copy-paste ready
7. REMEDIATION ROADMAP — prioritized fixes: Critical → High → Medium, with effort estimate
8. RESPONSIBLE DISCLOSURE — disclosure timeline (0-day, 7-day, 30-day, 90-day), notification process, CVE filing
9. COMPLIANCE MAPPING — map findings to OWASP Top 10, MITRE ATT&CK, NIST CSF controls

Always emphasize this is for authorized, educational red-team research with explicit written permission.`,
    buildUserPrompt: ({ target, framework, scope }, history) => {
      const parts = history.map((h) => `[${h.role}]\n${h.content}`).join("\n\n---\n\n");
      return `Target: "${target}"\nFramework: ${framework}\nScope: ${scope}\n\nSpecialist reports:\n\n${parts}\n\nSynthesize the complete security assessment document.`;
    },
  },
];

router.post("/cyber/assess", async (req, res) => {
  const { target, scope, attackSurface, protocol, browserTarget, intensity, framework, session_id } = req.body ?? {};

  if (!target || typeof target !== "string" || target.trim().length === 0 || target.length > 2000) {
    res.status(400).json({ error: "Invalid request: target is required (max 2000 chars)" });
    return;
  }
  if (!session_id || typeof session_id !== "string") {
    res.status(400).json({ error: "Invalid request: session_id is required" });
    return;
  }

  void session_id;

  const input: CyberInput = {
    target: target.trim(),
    scope: (scope as string) || "Web application",
    attackSurface: (attackSurface as string) || "HTTP/HTTPS endpoints",
    protocol: (protocol as string) || "TLS 1.3",
    browserTarget: (browserTarget as string) || "Chrome 120",
    intensity: (intensity as string) || "Moderate",
    framework: (framework as string) || "OWASP / MITRE ATT&CK",
  };

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);
  const history: AgentTurn[] = [];

  try {
    for (const agent of CYBER_AGENTS) {
      send({ type: "agent_start", agent: agent.id, role: agent.role, tool: agent.tool, color: agent.color });

      const userPrompt = agent.buildUserPrompt(input, history);
      let fullContent = "";

      const stream = await openai.chat.completions.create({
        model: "gpt-5.2",
        max_completion_tokens: 8192,
        messages: [
          { role: "system", content: agent.systemPrompt },
          { role: "user", content: userPrompt },
        ],
        stream: true,
      });

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          fullContent += content;
          send({ type: "token", agent: agent.id, content });
        }
      }

      history.push({ agent: agent.id, role: agent.role, content: fullContent });
      send({ type: "agent_done", agent: agent.id });
    }

    send({ type: "done" });
  } catch (err) {
    console.error("Cyber crew error:", err);
    send({ type: "error", message: "Cyber assessment pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
