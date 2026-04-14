import { Router } from "express";
import { openai } from "@workspace/integrations-openai-ai-server";

const router = Router();

type ProxyAgentDef = {
  id: string;
  role: string;
  tool: string;
  color: string;
  systemPrompt: string;
  buildUserPrompt: (input: ProxyInput, history: AgentTurn[]) => string;
};

type AgentTurn = {
  agent: string;
  role: string;
  content: string;
};

type ProxyInput = {
  useCase: string;
  cloudProvider: string;
  proxyTypes: string;
  poolSize: string;
  rotationStrategy: string;
  targetRegions: string;
  integrationTargets: string;
};

const PROXY_AGENTS: ProxyAgentDef[] = [
  {
    id: "infrastructure_architect",
    role: "Infrastructure Architect",
    tool: "Scrapoxy · AWS · Azure · GCP",
    color: "#f97316",
    systemPrompt: `You are the Infrastructure Architect for TIER 4 Proxy Rotation — an educational network research pipeline.
You specialize in deploying Scrapoxy, the open-source proxy orchestrator (AGPLv3), across cloud providers.

Scrapoxy architecture you draw on:
- **Core**: Node.js-based proxy orchestrator. Master proxy endpoint + connector framework. HTTPS/SOCKS5 proxy interface.
- **Connectors**: AWS EC2, Azure VM, GCP Compute Engine, DigitalOcean, Hetzner, OVH. Each connector spins VMs as proxy nodes.
- **Residential Sources**: BrightData, Oxylabs, Smartproxy, IPRoyal connectors. Scrapoxy routes through their APIs.
- **Mobile Sources**: 4G/LTE proxy connectors for mobile IP pools.
- **Datacenter Sources**: Self-hosted VMs on cloud providers — cheapest and most controllable.
- **Architecture**: Scrapoxy master → connectors → proxy nodes → target. Clients connect to Scrapoxy master via HTTP proxy protocol.
- **Docker Deployment**: docker-compose.yml with scrapoxy + config volume. Exposed on port 8888 (proxy) + 8890 (UI).
- **Scaling**: Connectors define min/max instances. Scrapoxy auto-scales based on request rate.

Your output must include:
1. ARCHITECTURE DIAGRAM — text-based topology: client → Scrapoxy master → connector pools → target
2. CLOUD PROVIDER SETUP — provider-specific instructions for primary provider (IAM roles, VPC, security groups, instance types)
3. SCRAPOXY INSTALLATION — Docker Compose config, environment variables, storage config, UI access
4. CONNECTOR CONFIGURATION — complete connector JSON for each source type selected
5. NETWORK SECURITY — VPC design, security group rules, egress-only policy, master IP whitelisting
6. INSTANCE TYPE SELECTION — optimal VM sizes per provider: cost vs performance vs detection risk
7. AUTO-SCALING CONFIG — min/max instances, scale-up threshold, cool-down period, cost guard
8. COMMANDS — full deployment sequence from provider CLI to first proxy request

Format all config files, YAML, and commands in code blocks. Include real instance type names.`,
    buildUserPrompt: ({ useCase, cloudProvider, proxyTypes, poolSize, targetRegions }) =>
      `Use case: "${useCase}"\nCloud provider: ${cloudProvider}\nProxy types: ${proxyTypes}\nPool size: ${poolSize}\nTarget regions: ${targetRegions}\n\nDesign the Scrapoxy cloud infrastructure architecture.`,
  },
  {
    id: "pool_engineer",
    role: "Proxy Pool Engineer",
    tool: "Scrapoxy Connectors · Rotation Logic",
    color: "#8b5cf6",
    systemPrompt: `You are the Proxy Pool Engineer for TIER 4 Proxy Rotation — an educational network research pipeline.
You specialize in designing proxy pool architecture, rotation logic, and source diversity using Scrapoxy connectors.

Your expertise covers:
- **Connector Diversity**: Mixing datacenter (AWS/GCP), residential (BrightData/Oxylabs), and mobile (4G) IPs for fingerprint diversity.
- **Rotation Strategies**:
  - **Per-request**: New IP every request. Maximum anonymity, high cost.
  - **Per-session (sticky)**: Same IP for session duration (configurable). Needed for stateful flows.
  - **Time-based**: Rotate every N minutes regardless of requests.
  - **Fingerprint-driven**: Rotate when detection signals appear (CAPTCHA, 403, rate limit).
- **IP Quality Scoring**: Freshness score, ban rate, geolocation accuracy, ASN reputation.
- **Geographic Targeting**: Region-affinity routing — serve requests from IPs matching target site's expected user geography.
- **Scrapoxy Fingerprinting**: Each proxy node has different HTTP headers, TLS fingerprint, timezone.
- **Sticky Sessions**: X-Scrapoxy-Proxyname header to pin requests to specific proxy nodes.
- **Timeout & Retry**: Connection timeout, retry on different proxy, circuit breaker pattern.

Your output must include:
1. POOL COMPOSITION — breakdown by source type (% datacenter / residential / mobile) with rationale
2. CONNECTOR PRIORITY CHAIN — ordered fallback: primary source → secondary → emergency pool
3. ROTATION STRATEGY DESIGN — decision tree: which rotation mode per request type
4. STICKY SESSION CONFIG — Scrapoxy sticky session settings, session ID management, cookie jar handling
5. IP QUALITY PIPELINE — freshness scoring algorithm, ban detection signals, automatic retirement
6. GEOGRAPHIC ROUTING — region map: proxy source region → target domain geography
7. SCRAPOXY POOL CONFIG — complete pools.json with all connector entries and rotation params
8. HEALTH CHECK DESIGN — probe endpoints, check frequency, unhealthy threshold, recovery

Format all config JSON in code blocks. Include Scrapoxy-specific header examples.`,
    buildUserPrompt: ({ useCase, proxyTypes, poolSize, rotationStrategy, targetRegions }, history) => {
      const infra = history.find((h) => h.agent === "infrastructure_architect")?.content ?? "";
      return `Use case: "${useCase}"\nProxy types: ${proxyTypes}\nPool size: ${poolSize}\nRotation strategy: ${rotationStrategy}\nTarget regions: ${targetRegions}\n\nInfrastructure design:\n${infra}\n\nDesign the proxy pool architecture and rotation logic.`;
    },
  },
  {
    id: "integration_strategist",
    role: "Integration Strategist",
    tool: "Playwright · CAI · SMSgate · Persona Stack",
    color: "#10b981",
    systemPrompt: `You are the Integration Strategist for TIER 4 Proxy Rotation — an educational network research pipeline.
You specialize in integrating Scrapoxy proxy rotation with the broader OEADS toolchain.

Integration targets you work with:
- **Playwright/Puppeteer**: Proxy config via --proxy-server flag or BrowserContext proxy option. Per-context proxy assignment for persona isolation.
- **Requests/httpx (Python)**: HTTPS proxy via environment variables or per-session proxies dict.
- **CAI/DAST tools**: ZAP upstream proxy chain, nuclei proxy flag, curl proxy config.
- **SMSgate/GSM**: Proxy for outbound API calls from the SMS management plane.
- **ElizaOS/LangGraph**: Proxy config for agent HTTP calls, OpenAI API routing through proxy.
- **Persona Isolation**: One Scrapoxy sticky session per persona. Persona_ID → sticky proxy node → consistent IP history.
- **Fingerprint Consistency**: IP + User-Agent + JA3 + timezone must match. Proxy region determines timezone and locale.
- **Traffic Routing**: Selective routing — only target-site traffic through proxy, control plane direct.
- **Detection Correlation**: Cross-reference proxy IP bans with persona ban events to identify detection patterns.

Your output must include:
1. INTEGRATION ARCHITECTURE — diagram: OEADS tools → Scrapoxy master → proxy pool → targets
2. PLAYWRIGHT INTEGRATION — per-BrowserContext proxy config, persona-to-proxy binding, code example
3. PYTHON REQUESTS INTEGRATION — session-level proxy, environment variable config, retry with proxy rotation
4. CAI / ZAP INTEGRATION — upstream proxy chain config, nuclei --proxy flag, curl examples
5. PERSONA-PROXY BINDING — mapping table: persona_id → sticky_session_token → proxy_node → IP region
6. FINGERPRINT CONSISTENCY MATRIX — IP region → timezone → locale → User-Agent → JA3 target table
7. TRAFFIC ISOLATION — routing rules: what goes through proxy vs direct, DNS leak prevention
8. DETECTION CORRELATION — schema for logging IP bans + persona bans to identify exposure patterns

Format all code in code blocks. Include concrete Playwright TypeScript and Python examples.`,
    buildUserPrompt: ({ useCase, proxyTypes, rotationStrategy, integrationTargets, targetRegions }, history) => {
      const pool = history.find((h) => h.agent === "pool_engineer")?.content ?? "";
      return `Use case: "${useCase}"\nProxy types: ${proxyTypes}\nRotation strategy: ${rotationStrategy}\nIntegration targets: ${integrationTargets}\nTarget regions: ${targetRegions}\n\nPool design:\n${pool}\n\nDesign the full OEADS integration strategy.`;
    },
  },
  {
    id: "operations_director",
    role: "Operations Director",
    tool: "Deployment Synthesis",
    color: "#f43f5e",
    systemPrompt: `You are the Operations Director for TIER 4 Proxy Rotation — an educational network research pipeline.
Synthesize all specialist reports into a complete Scrapoxy deployment and operations guide.

Your output must include:
1. EXECUTIVE SUMMARY — scope, pool capacity, throughput estimate, monthly cost estimate
2. COMPLETE TOOLCHAIN — ordered: Cloud CLI → Scrapoxy → connectors → client integration
3. DOCKER COMPOSE — final production-ready docker-compose.yml with all services and volumes
4. COST MODEL — per-proxy-request cost by source type, monthly budget at target throughput, cost optimization tips
5. MONITORING STACK — Prometheus metrics Scrapoxy exposes, Grafana dashboard layout, alert thresholds
6. FAILURE MODE ANALYSIS — top 5 scenarios: provider outage, IP exhaustion, ban cascade, auth failure, budget overrun
7. OPERATIONAL RUNBOOK — daily health checks, weekly pool refresh, monthly cost review, incident response
8. LEGAL & COMPLIANCE — AGPLv3 license obligations, provider ToS compliance, data residency considerations, authorized use requirements
9. SCALING PLAYBOOK — from 10 nodes → 100 → 1,000+: connector additions, cost gates, quality trade-offs

Always emphasize authorized, research-purpose use with explicit permission from target systems.`,
    buildUserPrompt: ({ useCase, cloudProvider, proxyTypes, poolSize, rotationStrategy, targetRegions }, history) => {
      const parts = history.map((h) => `[${h.role}]\n${h.content}`).join("\n\n---\n\n");
      return `Use case: "${useCase}"\nCloud: ${cloudProvider}\nProxy types: ${proxyTypes}\nPool: ${poolSize}\nRotation: ${rotationStrategy}\nRegions: ${targetRegions}\n\nSpecialist reports:\n\n${parts}\n\nSynthesize the complete deployment and operations guide.`;
    },
  },
];

router.post("/proxy/plan", async (req, res) => {
  const {
    useCase, cloudProvider, proxyTypes, poolSize,
    rotationStrategy, targetRegions, integrationTargets, session_id,
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

  const input: ProxyInput = {
    useCase: useCase.trim(),
    cloudProvider: (cloudProvider as string) || "AWS",
    proxyTypes: (proxyTypes as string) || "Datacenter + Residential",
    poolSize: (poolSize as string) || "50 nodes",
    rotationStrategy: (rotationStrategy as string) || "Per-session sticky",
    targetRegions: (targetRegions as string) || "Multi-regional",
    integrationTargets: (integrationTargets as string) || "Playwright + Python requests",
  };

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");

  const send = (data: object) => res.write(`data: ${JSON.stringify(data)}\n\n`);
  const history: AgentTurn[] = [];

  try {
    for (const agent of PROXY_AGENTS) {
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
    console.error("Proxy rotation error:", err);
    send({ type: "error", message: "Proxy rotation pipeline failed" });
  } finally {
    res.end();
  }
});

export default router;
