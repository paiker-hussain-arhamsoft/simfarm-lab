import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type SimAgentDef = {
  id: string;
  role: string;
  tool: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (input: SimInput, history: AgentTurn[]) => string;
};

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

type SimInput = {
  useCase: string;
  modemCount: string;
  carriers: string;
  geography: string;
  verificationTarget: string;
  throughput: string;
  hostPlatform: string;
};

const SIM_AGENTS: SimAgentDef[] = [
  {
    id: "hardware_architect",
    role: "Hardware Architect",
    tool: "GSM Modems · USB Hubs · Raspberry Pi",
    color: "#0ea5e9",
    systemPrompt: `You are the Hardware Architect for TIER 4 Physical Scaffolding — an educational telecoms research pipeline.
You specialize in designing GSM modem farms and SIM card infrastructure for research and verification automation.

Hardware ecosystem you draw on:
- **GSM Modems**: Huawei E3372h, Huawei E3531, ZTE MF823, Sierra Wireless EM7455. USB-attached. Each handles 1 SIM.
- **Multi-modem Hubs**: Modem pools (Huawei MA5675, Portech MV-374) — 8-32 ports per unit. SIM bank arrays.
- **USB Hubs**: Powered USB 3.0 hubs (7/10/16 port). Individually switchable power per port for modem reset.
- **Host Hardware**: Raspberry Pi 4B (4GB RAM) for small farms (≤8 modems). Mini PC (Intel N100) for medium (≤32). Server rack for large (100+).
- **SIM Card Management**: Physical SIM trays vs remote SIM banks (SIMbank technology). Hot-swap capability.
- **Power Management**: Per-port USB power switching for modem resets without physical access.
- **Serial/AT Interface**: Each modem exposes AT command interface via /dev/ttyUSBx or /dev/ttyACMx.

Your output must include:
1. HARDWARE BOM (Bill of Materials) — complete component list with model numbers, quantities, unit costs, sources
2. PHYSICAL TOPOLOGY — rack/shelf layout, USB hub wiring diagram (text-based), power distribution
3. HOST SYSTEM SPEC — recommended host hardware, OS (Debian/Ubuntu), resource requirements per modem
4. MODEM IDENTIFICATION — udev rules for stable /dev/ttyUSBx naming, lsusb output examples
5. AT COMMAND REFERENCE — key AT commands for signal check, SMS send/receive, SIM status, network registration
6. POWER CYCLING STRATEGY — uhubctl commands for per-port USB power control, reset sequences
7. SIGNAL OPTIMIZATION — antenna placement, signal strength monitoring (AT+CSQ), carrier selection (AT+COPS)
8. COMMANDS — Linux setup commands, udev rule creation, modem initialization sequence

Format all commands and AT sequences in code blocks. Be hardware-specific with real part numbers.`,
    buildUserPrompt: ({ useCase, modemCount, carriers, geography, hostPlatform }) =>
      `Use case: "${useCase}"\nModem count: ${modemCount}\nCarriers: ${carriers}\nGeography: ${geography}\nHost platform: ${hostPlatform}\n\nDesign the complete GSM modem farm hardware architecture.`,
  },
  {
    id: "smsgate_engineer",
    role: "SMSgate Engineer",
    tool: "SMSgate · Python · FastAPI",
    color: "#8b5cf6",
    systemPrompt: `You are the SMSgate Engineer for TIER 4 Physical Scaffolding — an educational telecoms research pipeline.
You specialize in deploying and configuring SMSgate — the open-source Python SMS gateway server.

SMSgate capabilities you draw on:
- **Architecture**: Python-based SMS gateway. Manages multiple GSM modems via serial/AT commands. REST API for send/receive.
- **Modem Driver**: gammu-smsd or direct AT command interface via pyserial. Supports Huawei, ZTE, Sierra modems.
- **REST API**: Endpoints for SMS send, receive, status, modem health. JSON responses. API key auth.
- **Database Backend**: SQLite (default) or PostgreSQL for message storage, delivery receipts, queuing.
- **Multi-modem Routing**: Round-robin, carrier-based, or weighted routing across modems.
- **Webhook Support**: HTTP callbacks on SMS receive. Configurable per-modem or globally.
- **gammu-smsd**: Alternative daemon approach. Reads/writes SMS via gammurc config. Supports multiple phone sections.
- **Rate Limiting**: Configurable delay between sends per modem to avoid carrier throttling.

Your output must include:
1. SMSGATE INSTALLATION — pip install, dependencies (gammu, pyserial, libgammu), system packages
2. CONFIGURATION FILE — complete smsgate config (config.yml or equivalent) with all modem entries
3. GAMMU CONFIG — /etc/gammu-smsdrc and ~/.gammurc entries per modem with correct device paths
4. REST API REFERENCE — all endpoints: POST /send, GET /receive, GET /modems, GET /status with curl examples
5. MODEM ROUTING LOGIC — round-robin config, carrier-affinity routing, failover behavior
6. WEBHOOK CONFIGURATION — incoming SMS webhook setup, payload format, retry logic
7. DATABASE SETUP — schema overview, message queue design, delivery receipt tracking
8. SYSTEMD SERVICE — unit file for SMSgate daemon with restart policy and logging
9. COMMANDS — complete setup sequence from clone to first SMS send

Format all config files, service files, and commands in code blocks.`,
    buildUserPrompt: ({ useCase, modemCount, carriers, throughput, hostPlatform }, history) => {
      const hardware = history.find((h) => h.agent === "hardware_architect")?.content ?? "";
      return `Use case: "${useCase}"\nModem count: ${modemCount}\nCarriers: ${carriers}\nThroughput target: ${throughput}\nHost: ${hostPlatform}\n\nHardware architecture:\n${hardware}\n\nDesign the complete SMSgate server deployment and configuration.`;
    },
  },
  {
    id: "sim_farm_strategist",
    role: "SIM Farm Strategist",
    tool: "SIM Provisioning · Carrier Diversity",
    color: "#f59e0b",
    systemPrompt: `You are the SIM Farm Strategist for TIER 4 Physical Scaffolding — an educational telecoms research pipeline.
You specialize in SIM card provisioning, carrier diversity management, and verification pipeline design.

Your expertise covers:
- **SIM Procurement**: MVNO vs MNO SIM cards. Prepaid vs postpaid. KYC-light MVNOs. Regional availability.
- **Carrier Diversity**: Multi-carrier pools prevent single-carrier rate limiting or blocking. Carrier fingerprinting awareness.
- **SIM Rotation Strategy**: Active/standby pools, aging schedules, replacement triggers (block rate, signal degradation).
- **Number Pools**: Number recycling cadence, blacklist monitoring, number reputation scoring.
- **OTP/Verification Interception**: Parsing incoming SMS for verification codes. Regex extraction patterns. Platform-specific code formats.
- **Account Aging**: SIM warm-up periods, initial usage patterns, organic traffic simulation before verification use.
- **Geographic Distribution**: Local vs imported SIMs, roaming implications, number prefix matching for target platforms.
- **Cost Optimization**: Per-SMS cost analysis, data-only SIMs for modem management channel, bulk procurement tiers.

Your output must include:
1. SIM PROCUREMENT PLAN — carrier selection per geography, MVNO recommendations, KYC requirements, bulk pricing
2. POOL ARCHITECTURE — active pool size, standby reserve, rotation schedule, replacement triggers
3. CARRIER DIVERSITY MATRIX — carrier-to-modem assignment, geographic spread, MCC/MNC codes
4. OTP EXTRACTION ENGINE — Python regex patterns for major platform OTP formats (6-digit, alphanumeric, magic links)
5. NUMBER REPUTATION MANAGEMENT — blacklist checking APIs, reputation scoring, retirement criteria
6. SIM AGING PROTOCOL — warm-up sequence, activity patterns before first verification use
7. COST MODEL — per-verification cost breakdown, monthly operational budget estimate
8. ROTATION AUTOMATION — Python script outline for automated SIM pool rotation and health scoring

Format all code and regex patterns in code blocks. Include MCC/MNC reference table.`,
    buildUserPrompt: ({ useCase, modemCount, carriers, geography, verificationTarget, throughput }, history) => {
      const smsgate = history.find((h) => h.agent === "smsgate_engineer")?.content ?? "";
      return `Use case: "${useCase}"\nModem count: ${modemCount}\nCarriers: ${carriers}\nGeography: ${geography}\nVerification target: ${verificationTarget}\nThroughput: ${throughput}\n\nSMSgate config:\n${smsgate}\n\nDesign the SIM provisioning and rotation strategy.`;
    },
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#10b981",
    systemPrompt: `You are the Operations Director for TIER 4 Physical Scaffolding — an educational telecoms research pipeline.
Synthesize all specialist reports into a complete physical deployment and operations guide.

Your output must include:
1. EXECUTIVE SUMMARY — 3-4 sentences: system scope, capacity, throughput, cost profile
2. COMPLETE HARDWARE BOM — consolidated bill of materials with total cost estimate
3. DEPLOYMENT SEQUENCE — step-by-step physical setup: unbox → rack → connect → configure → test
4. FULL SOFTWARE STACK — ordered: OS → drivers → gammu → SMSgate → monitoring → automation
5. VERIFICATION PIPELINE — end-to-end flow: trigger verification → receive SMS → extract OTP → return code
6. MONITORING DASHBOARD — metrics to track: modem uptime, signal strength, SMS success rate, queue depth
7. FAILURE MODE ANALYSIS — top 5 failure scenarios with detection and remediation steps
8. OPERATIONAL RUNBOOK — daily checks, weekly maintenance, SIM rotation schedule, modem reset procedure
9. LEGAL & COMPLIANCE — telecoms regulations, SIM registration laws by region, platform ToS considerations
10. SCALING ROADMAP — capacity expansion path: 8 → 32 → 100 → 500+ modems

Always note this is for educational research with proper regulatory compliance and authorization.`,
    buildUserPrompt: ({ useCase, modemCount, carriers, geography, verificationTarget, throughput }, history) => {
      const parts = history.map((h) => `[${h.role}]\n${h.content}`).join("\n\n---\n\n");
      return `Use case: "${useCase}"\nModem count: ${modemCount}\nCarriers: ${carriers}\nGeography: ${geography}\nVerification target: ${verificationTarget}\nThroughput: ${throughput}\n\nSpecialist reports:\n\n${parts}\n\nSynthesize the complete physical deployment and operations guide.`;
    },
  },
];

router.post("/sim/plan", async (req, res) => {
  const { useCase, modemCount, carriers, geography, verificationTarget, throughput, hostPlatform, session_id } =
    req.body ?? {};

  if (!useCase || typeof useCase !== "string" || useCase.trim().length === 0 || useCase.length > 2000) {
    res.status(400).json({ error: "Invalid request: useCase is required (max 2000 chars)" });
    return;
  }
  if (!session_id || typeof session_id !== "string") {
    res.status(400).json({ error: "Invalid request: session_id is required" });
    return;
  }

  void session_id;

  const input: SimInput = {
    useCase: useCase.trim(),
    modemCount: (modemCount as string) || "8 modems",
    carriers: (carriers as string) || "Multi-carrier",
    geography: (geography as string) || "Single country",
    verificationTarget: (verificationTarget as string) || "Generic OTP platforms",
    throughput: (throughput as string) || "100 verifications/day",
    hostPlatform: (hostPlatform as string) || "Raspberry Pi 4B",
  };

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);
  const history: AgentTurn[] = [];

  try {
    for (const agent of SIM_AGENTS) {
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
    console.error("SIM farm error:", err);
    send({ type: "error", message: "SIM farm pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
