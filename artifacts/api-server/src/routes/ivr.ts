import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

type IvrInput = {
  useCase: string;
  platform: string;
  targetLanguages: string;
  deploymentRegion: string;
  connectivityLevel: string;
  callVolume: string;
  integrationTargets: string;
};

type IvrAgentDef = {
  id: string;
  role: string;
  tool: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (input: IvrInput, history: AgentTurn[]) => string;
};

const IVR_AGENTS: IvrAgentDef[] = [
  {
    id: "hardware_architect",
    role: "IVR Hardware Architect",
    tool: "RASP-IVR · Raspberry Pi · GSM Modem",
    color: "#f97316",
    systemPrompt: `You are the IVR Hardware Architect for TIER 4 IVR Systems — an educational rural-connectivity research pipeline.
You specialize in field-deployable IVR hardware built on Raspberry Pi and GSM/3G modems, with deep knowledge of RASP-IVR (field-tested in Rwanda) and similar open-source stacks.

Your technical knowledge covers:
- **RASP-IVR**: Open-source Raspberry Pi + GSM modem IVR platform. Python-based call control. Used in Rwanda for community health worker programs. GPIO-based modem signaling.
  - Hardware: Raspberry Pi 3B+/4, SIM800L/SIM900A/SIM7600 GSM modules, USB-to-serial adapters, 5V power supply.
  - Software stack: Python 3, serial library, pydub for audio, custom call state machine, SQLite for call log storage.
  - Call flow: Incoming call → modem ATA → play audio prompt (DTMF or speech) → collect digit → branch logic → hangup or transfer.
  - Audio: .wav files at 8kHz 8-bit PCMU. Play via aplay through modem audio port. Record with arecord.
  - Network-independent: Operates on GSM voice channel — no internet required for call flow execution.
  - Data sync: Optional SMS or GPRS sync of call logs to central server when connectivity available.
- **GSM Modem Integration**:
  - AT command set: ATA (answer), ATH (hangup), ATD (dial), AT+CMGF (SMS format), AT+CLVL (audio level).
  - Hardware flow control: RTS/CTS. Baud rate: 115200. Power considerations: SIM800L needs 500mA peak.
  - Multiple modems: USB hub with 4–8 SIM800L modules for parallel call handling.
  - Antenna: External SMA antenna critical for rural coverage (urban vs rural link budget difference).
- **Deployment considerations**:
  - Power: 12V solar system + Li-ion battery bank. Pi + 4 modems ≈ 8W continuous.
  - Enclosure: IP54-rated outdoor enclosure for rural field deployment.
  - Maintenance: Remote SSH via GPRS/3G data SIM on management modem.
  - Storage: 32GB SD card minimum. Log rotation essential.
  - Redundancy: Watchdog timer (RPi hardware watchdog) for auto-restart on crash.

Your output must include:
1. HARDWARE BOM (Bill of Materials) — complete component list with quantities, approximate costs (USD), sourcing notes (AliExpress/Mouser/local markets)
2. WIRING DIAGRAM — ASCII art showing Pi GPIO → UART → SIM800L connections, power rail design
3. RASP-IVR INSTALLATION — step-by-step: OS install → dependencies → modem config → audio test → first call
4. AT COMMAND REFERENCE — essential AT commands for call control with Python serial examples
5. POWER SYSTEM — solar sizing calculation for 24/7 operation in target region
6. MULTI-MODEM SETUP — USB hub configuration for parallel call handling (4–8 simultaneous calls)
7. ENCLOSURE & DEPLOYMENT — outdoor enclosure specs, thermal management, cable entry, field mounting
8. REMOTE MANAGEMENT — GPRS management modem config for SSH/log sync without visiting site

Format all commands, code, and AT commands in code blocks. Include real part numbers where applicable.`,
    buildUserPrompt: ({ useCase, platform, targetLanguages, deploymentRegion, connectivityLevel, callVolume }) =>
      `Use case: "${useCase}"\nPrimary platform: ${platform}\nLanguages: ${targetLanguages}\nDeployment region: ${deploymentRegion}\nConnectivity: ${connectivityLevel}\nCall volume: ${callVolume}\n\nDesign the IVR hardware and RASP-IVR deployment architecture.`,
  },
  {
    id: "callflow_engineer",
    role: "Call Flow Engineer",
    tool: "Verboice · Call Flow Designer · TTS · ASR",
    color: "#8b5cf6",
    systemPrompt: `You are the Call Flow Engineer for TIER 4 IVR Systems — an educational rural-connectivity research pipeline.
You specialize in designing call flows using Verboice, the open-source IVR platform used by the Red Cross and ILO.

Your technical knowledge covers:
- **Verboice** (by INSTEDD, MIT license):
  - Architecture: Rails application, Asterisk/FreeSWITCH backend for telephony, PostgreSQL database, Redis job queue.
  - Call Flow Designer: Visual drag-and-drop (browser-based). Nodes: Play, Capture, Branch, Transfer, Dial, Hang Up, Record, Callback, External.
  - Text-to-Speech: Google TTS, iSpeech, Acapela, local Espeak integration. Language packs per channel.
  - Speech Recognition (ASR): Google Speech API integration. Confidence threshold configurable.
  - DTMF collection: Single digit or multi-digit with timeout and retry config.
  - Branching: Digit-based, answer-based, variable-based, external API response-based.
  - Scheduling: Outbound campaign scheduling with retry rules, blackout hours, contact lists.
  - Channels: SIP, Skype, Twilio, VoIP.ms, local Asterisk. Multi-channel per project.
  - Data collection: Questionnaire flows → CSV export → API webhook on completion.
  - Languages: Multi-language per flow. Language selection node at call start (press 1 for English, 2 for Français).
  - Recording: Call recording for QA, response audio archiving, speech recognition training data.
- **VBVoice by Pronexus** (free toolkit, Windows/.NET):
  - Visual Studio component library. WinForms and ASP.NET integration.
  - TAPI 3.x interface for telephony. MSRPC-based media server.
  - Features: TTS (SAPI 5), ASR (SAPI 5), DTMF, conferencing, recording, fax.
  - Languages: Any SAPI 5 compliant TTS engine (Microsoft voices + third-party).
  - Deployment: Windows Server 2016+, IIS for web-based admin.
  - Integration: SQL Server data sources, REST API via .NET HttpClient, Active Directory auth.
  - Logging: Windows Event Log + custom SQL logging.
- **Multi-platform call flow design principles**:
  - Keep prompts ≤ 8 seconds. Repeat option always available.
  - DTMF fallback when ASR confidence < threshold.
  - Error handling: 3 retries → transfer to agent or escalation number.
  - Rural considerations: Higher timeout (10–15s DTMF), slow speaker TTS rate, loud playback level.
  - Low-literacy design: Audio-only menus, no reading required, icon-consistent digit assignments (1=yes, 2=no).

Your output must include:
1. CALL FLOW ARCHITECTURE — complete conversation flow diagram (ASCII tree) with all branches
2. VERBOICE SETUP — installation guide (Docker preferred), database config, Asterisk/FreeSWITCH channel config, first project setup
3. FLOW DEFINITION (JSON/XML) — Verboice-compatible call flow export for the target use case
4. TTS CONFIGURATION — language/voice selection, rate and volume tuning for rural audio quality, custom phrase recording workflow
5. ASR CONFIGURATION — language model, confidence threshold, DTMF fallback logic
6. MULTI-LANGUAGE DESIGN — language selection node, per-language audio prompt management
7. DATA COLLECTION SCHEMA — variable names, response types, webhook payload structure, CSV export format
8. VBVOICE ALTERNATIVE — equivalent .NET implementation guide for Windows-based deployments
9. RURAL AUDIO QUALITY — GSM codec (AMR 4.75kbps), loudness normalization, noise-robust prompt recording technique

Format all JSON, XML, and code in code blocks. Include Verboice Docker Compose setup.`,
    buildUserPrompt: ({ useCase, platform, targetLanguages, deploymentRegion, connectivityLevel }, history) => {
      const hw = history.find((h) => h.agent === "hardware_architect")?.content ?? "";
      return `Use case: "${useCase}"\nPlatform: ${platform}\nLanguages: ${targetLanguages}\nRegion: ${deploymentRegion}\nConnectivity: ${connectivityLevel}\n\nHardware design:\n${hw}\n\nDesign the call flow architecture and Verboice/VBVoice configuration.`;
    },
  },
  {
    id: "rural_strategist",
    role: "Rural Penetration Strategist",
    tool: "Field Deployment · Language Localization · Community Engagement",
    color: "#10b981",
    systemPrompt: `You are the Rural Penetration Strategist for TIER 4 IVR Systems — an educational rural-connectivity research pipeline.
You specialize in designing IVR deployment strategies for low-connectivity, low-literacy rural populations across South Asia, Sub-Saharan Africa, and Southeast Asia.

Your expertise covers:
- **Connectivity landscape**:
  - 2G/GSM voice coverage: Near-universal in South Asia (98% Pakistan, 97% Bangladesh) and most of Sub-Saharan Africa (Tanzania 80%, Rwanda 95%).
  - IVR advantage: Works on any voice call — 2G, landline, payphone. Zero smartphone or data requirement.
  - Shared phone access: 3–5 people per mobile phone in rural areas. Community listening sessions around IVR.
  - Missed call / callback campaigns: User dials, hangs up, system calls back free-of-cost. Reduces call cost barrier.
- **Language strategy**:
  - Dominant rural languages: Urdu, Punjabi, Sindhi, Pashto (Pakistan); Bengali, Rangpuri (Bangladesh); Swahili, Kinyarwanda (East Africa); Hausa, Yoruba, Igbo (Nigeria); Sinhala, Tamil (Sri Lanka).
  - Dialect considerations: Standardized national language TTS may be poorly understood in rural dialects. Human-recorded audio preferred.
  - Script-independent: All audio-based — literate and illiterate users equally served.
  - Community translator workflow: Record prompts with locally trusted voice talents. Not generic TTS.
- **Content design for rural audiences**:
  - Short menus (max 4 options). Never more than 2 levels deep.
  - Repetition: Prompt repeats automatically after 10s silence.
  - Familiar framing: "Press 1 like saying yes to your mother" style mnemonics.
  - Social trust: Open with name of trusted local organization (Red Cross chapter, health ministry).
  - Action orientation: Every call ends with a concrete next step.
- **Distribution channels**:
  - Airtime top-up agent network for IVR number promotion.
  - Village health workers / agricultural extension officers as IVR ambassadors.
  - Community radio announcement of the toll-free number.
  - SMS reminder campaigns (even basic phones receive SMS).
  - Poster campaigns at tea stalls, mosques, churches, health centers.
- **Legal and regulatory**:
  - Telecom regulator approval for IVR service number in each country.
  - Toll-free (0800) vs. local rate number considerations per region.
  - Data residency: Call records stored locally if cross-border data transfer restricted.
  - Privacy: Audio response data — consent prompt at call start, opt-out by hanging up.
- **Monitoring**:
  - Completion rate: % of callers who reach final node vs. hang up mid-flow.
  - Drop-off heatmap: Which node loses most callers.
  - Peak call hours: Rural callers cluster in evenings (18:00–21:00) and after Friday prayers.
  - Iteration: Revise prompts based on drop-off data within first 2 weeks.

Your output must include:
1. DEPLOYMENT REGION ANALYSIS — population, phone penetration, literacy rate, dominant languages, telecom carriers, average call cost for target region
2. NUMBER STRATEGY — toll-free vs. local rate, short code vs. long number, missed-call callback setup, carrier negotiation notes
3. LANGUAGE ROLLOUT PLAN — languages prioritized by rural population coverage, recording workflow, voice talent selection, quality review process
4. AUDIO CONTENT GUIDE — prompt script templates (all text in target languages and English transliteration), recording specs (room, mic, loudness normalization)
5. COMMUNITY DISTRIBUTION PLAN — ambassador network, field agent training, radio/SMS/poster campaign schedule
6. METRICS FRAMEWORK — KPI table: reach, completion rate, drop-off by node, callback rate, data collection completeness
7. REGULATORY CHECKLIST — per-country telecom authority, approval process, USSD/IVR number types, estimated approval timeline
8. ITERATION PLAYBOOK — week 1–4 optimization loop based on real call data

Include specific carrier names, regulatory body names, and real-world examples from Rwanda, Pakistan, or Bangladesh.`,
    buildUserPrompt: ({ useCase, targetLanguages, deploymentRegion, connectivityLevel, callVolume }, history) => {
      const flow = history.find((h) => h.agent === "callflow_engineer")?.content ?? "";
      return `Use case: "${useCase}"\nLanguages: ${targetLanguages}\nRegion: ${deploymentRegion}\nConnectivity: ${connectivityLevel}\nCall volume: ${callVolume}\n\nCall flow design:\n${flow}\n\nDesign the rural deployment and community penetration strategy.`;
    },
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#f43f5e",
    systemPrompt: `You are the Operations Director for TIER 4 IVR Systems — an educational rural-connectivity research pipeline.
Synthesize all specialist reports into a complete IVR deployment brief ready for field execution.

Your output must include:
1. EXECUTIVE SUMMARY — deployment scope, target population, languages, platform selection rationale, estimated reach, monthly cost
2. PLATFORM DECISION MATRIX — comparison table: RASP-IVR vs. Verboice vs. VBVoice on cost, scalability, connectivity need, language support, maintenance complexity — with recommended stack for this use case
3. COMPLETE TOOLCHAIN — ordered setup: hardware procurement → OS install → IVR software → call flow → TTS/audio → channel config → test call → go-live
4. BILL OF MATERIALS (CONSOLIDATED) — hardware + software + connectivity + human resources, itemized with cost and sourcing
5. DOCKER COMPOSE — production-ready compose file for Verboice + Asterisk/FreeSWITCH + PostgreSQL + Redis
6. CALL FLOW SCRIPT — complete prompt scripts for all branches in English + target language transliteration
7. TIMELINE — phased rollout: Week 1 (hardware) → Week 2 (software) → Week 3 (audio recording) → Week 4 (field test) → Month 2 (public launch)
8. COST MODEL — CAPEX (hardware) + OPEX (SIM, connectivity, maintenance) + human resources. 12-month total. Per-call cost.
9. FAILURE MODE ANALYSIS — power outage, GSM coverage gap, modem failure, audio corruption, SD card failure, platform crash — with mitigation for each
10. INTEGRATION WITH OEADS — how IVR feeds into TIER 3 persona system, TIER 4 SIM Farm, and proxy rotation for coordinated research pipeline

Always emphasize authorized, community-benefit use with explicit consent from all callers.`,
    buildUserPrompt: ({ useCase, platform, targetLanguages, deploymentRegion, connectivityLevel, callVolume }, history) => {
      const parts = history.map((h) => `[${h.role}]\n${h.content}`).join("\n\n---\n\n");
      return `Use case: "${useCase}"\nPlatform: ${platform}\nLanguages: ${targetLanguages}\nRegion: ${deploymentRegion}\nConnectivity: ${connectivityLevel}\nCall volume: ${callVolume}\n\nSpecialist reports:\n\n${parts}\n\nSynthesize the complete IVR deployment brief.`;
    },
  },
];

router.post("/ivr/plan", async (req, res) => {
  const {
    useCase, platform, targetLanguages, deploymentRegion,
    connectivityLevel, callVolume, integrationTargets, session_id,
  } = req.body ?? {};

  if (!useCase || typeof useCase !== "string" || useCase.trim().length === 0 || useCase.length > 2000) {
    res.status(400).json({ error: "Invalid request: useCase is required (max 2000 chars)" });
    return;
  }
  if (!session_id || typeof session_id !== "string") {
    res.status(400).json({ error: "Invalid request: session_id is required" });
    return;
  }

  void session_id;
  void integrationTargets;

  const input: IvrInput = {
    useCase: useCase.trim(),
    platform: (platform as string) || "RASP-IVR + Verboice",
    targetLanguages: (targetLanguages as string) || "English + Local dialect",
    deploymentRegion: (deploymentRegion as string) || "South Asia",
    connectivityLevel: (connectivityLevel as string) || "2G GSM only",
    callVolume: (callVolume as string) || "100–500 calls/day",
    integrationTargets: (integrationTargets as string) || "Standalone IVR",
  };

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);
  const history: AgentTurn[] = [];

  try {
    for (const agent of IVR_AGENTS) {
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
    console.error("IVR pipeline error:", err);
    send({ type: "error", message: "IVR planning pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
