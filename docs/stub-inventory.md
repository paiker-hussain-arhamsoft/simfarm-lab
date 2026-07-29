# SimFarm Lab — Stub & Integration Inventory

This document lists every simulated tool currently implemented in the platform, every technology/integration mentioned in user prompts or agent descriptions that is represented as a stub, and any real engines that were requested but remain uninstalled. It also records each tool's offline/online classification and where its flag is enforced.

## How to read the flags

- **Offline-only** — the tool returns a simulated result and can function with no internet.
- **Offline-primary / online-optional** — the tool prefers an offline implementation, but the prompt/agent description acknowledges an optional online provider that would only work with an explicit API key (e.g. ElevenLabs, HeyGen).
- **Online-optional** — the tool is described against an online-capable provider (e.g. Browserbase) but the stub still returns `simulated: true` and never calls out.

All tool results are guarded by `backend/tools/registry.py:80` (`safety.enforce_result`), which rejects any result where `simulated != true` or any real-activity flag (e.g. `real_pii`, `job_executed`) is set to `True`. Therefore every tool below is simulation-only at runtime.

## Implemented simulated tool stubs (87 total)

### TIER 1 · Analysis (4)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `index_dataset` | Dataset Indexer | LlamaIndex | offline-only | Stub returns fake top matches from a `crm`/`cdr` dataset. |
| `narrative_saturation_score` | Narrative Saturation Scorer | sentiment-engine | offline-only | Stub sentiment distribution for a target/region. |
| `behavior_forecast` | Voter Behavior Forecaster | LightGBM | offline-only | Synthetic turnout/segment scores. |
| `dialect_analysis` | Dialect & Culture Analyzer | Meta-Llama-3.1-8B | offline-only | Linguistic/cultural signal modeling for Shahmukhi/Saraiki. |

### TIER 2 · Media (9)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `clone_voice` | Voice Cloner | Chatterbox / Coqui / Bark + ElevenLabs (optional) | offline-primary / online-optional | Offline Chatterbox/Coqui/Bark preferred; ElevenLabs is the online optional fallback. |
| `generate_video` | Video Generator | Wan2.1 / CogVideoX / Open-Sora + HeyGen (optional) | offline-primary / online-optional | Offline T2V models preferred; HeyGen optional. |
| `render_avatar` | Digital Human Renderer | Duix-Avatar / Wav2Lip / Roop | offline-only | Photo+script lip-synced avatar. |
| `generate_media_package` | Media Package Generator | Wan2.1 + Chatterbox | offline-only | Combined video/voice placeholder. |
| `face_swap` | Face-Swap Engine | DeepFaceLab / FaceSwap / Deep-Live-Cam | offline-only | Consent-gated, simulated only. |
| `lip_sync` | Lip-Sync Engine | Wav2Lip / VideoRetalking | offline-only | Stub deepfake lip-sync pipeline. |
| `gfpgan_upscale` | Face Restore / Upscale | GFPGAN | offline-only | Face restoration placeholder. |
| `ffmpeg_pipeline` | FFmpeg Pipeline | FFmpeg | offline-only | Deterministic compositing/muxing. |
| `social_targeting` | Social Platform Targeter | social-intel | offline-only | Reach/sentiment estimates for a region. |

### TIER 2 · Cyber Security (6)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `recon_scan` | Attack-Surface Scanner | Nmap / OpenVAS | offline-only | `tool:` parameter can be `nmap` or `openvas`; both are stubs. |
| `dast_scan` | DAST Scanner | OWASP ZAP / Burp Suite | offline-only | `tool:` parameter can be `zap` or `burp`; both are stubs. |
| `ja3_fingerprint` | TLS Fingerprint Analyzer | Salesforce JA3 | offline-only | Blue-team fingerprint analysis concept. |
| `exploit_validate` | Vulnerability Validator | Metasploit | offline-only | Controlled validation concept; no exploitation. |
| `osint_lookup` | OSINT Exposure Mapper | OSINT | offline-only | Passive exposure mapping for owned assets. |
| `cai_redteam` | Automated Red-Team Orchestrator | CAI (Alias Robotics) | offline-only | Red-team orchestration concept. |

### TIER 3 · Persona Orchestration (6)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `persona_design` | Synthetic Persona Designer | ElizaOS | offline-only | 7-layer synthetic identity design. |
| `update_persona` | Persona Controller | ElizaOS | offline-only | Trait-adjustment concept. |
| `behavior_model` | Behavior Modeler | Botpress / LangGraph | offline-only | Behavioral modeling / interaction scripting. |
| `voice_dialect_map` | Voice & Dialect Mapper | Coqui / Chatterbox + ElevenLabs (optional) | offline-primary / online-optional | Offline TTS preferred; ElevenLabs optional mapping. |
| `browser_automation_plan` | Browser Automation Planner | Playwright / Puppeteer / Selenium | offline-only | Headless-automation planning; no real browser automation. |
| `fleet_orchestrate` | Persona Fleet Orchestrator | ElizaOS / Socioboard | offline-only | Multi-persona coordination / lifecycle. |

### TIER 4 · Infrastructure / SIM Farm (11)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `modem_topology` | Modem Topology | SIM800/SIM900 · Gammu | offline-only | Physical USB-HUB/modem topology. |
| `smsgate_config` | SMSGate Config | SMSgate · Gammu | offline-only | Gateway configuration concept. |
| `modem_control` | Modem Control | Gammu | offline-only | Modeled AT/PDU commands. |
| `sim_provision_plan` | SIM Provision Plan | carrier-provisioning | offline-only | Number provisioning concept. |
| `sim_activate` | SIM Activate | carrier-provisioning | offline-only | SIM activation concept. |
| `carrier_access` | Carrier Access | carrier-API | offline-only | Carrier API access concept. |
| `campaign_orchestrate` | Campaign Orchestrator | Celery | offline-only | Campaign queue orchestration concept. |
| `sms_send` | SMS Send | SMSgate | offline-only | SMS send concept. |
| `celery_dispatch` | Celery Dispatch | Celery | offline-only | Celery worker dispatch concept. |
| `adjust_load_balancer` | Load Balancer Controller | infra-control | offline-only | Cloud LB strategy concept. |
| `rotate_proxy` | Proxy Rotator | Scrapoxy | offline-only | Routing/proxy vector rotation concept. |

### TIER 4 · IVR (6)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `ivr_hardware_setup` | IVR Hardware Setup | Raspberry Pi · GSM · RASP-IVR | offline-only | Hardware topology concept. |
| `call_flow_design` | Call Flow Designer | Verboice | offline-only | Call tree / IVR menu design. |
| `dtmf_handler` | DTMF Handler | VBVoice | offline-only | DTMF handling policy concept. |
| `rural_reach_model` | Rural Reach Model | rural-reach | offline-only | Low-bandwidth/feature-phone targeting. |
| `call_route_plan` | Call Route Planner | call-routing | offline-only | Call routing / queue concept. |
| `ivr_cost_model` | IVR Cost Model | cost-model | offline-only | Per-call cost model. |

### TIER 4 · Proxy Rotation (7)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `scrapoxy_deploy` | Scrapoxy Deploy | Scrapoxy · Docker | offline-only | Docker deployment concept. |
| `cloud_connector` | Cloud Connector | cloud-connectors | offline-only | Cloud provider connector concept. |
| `proxy_pool_size` | Proxy Pool Sizer | pool-sizing | offline-only | Pool-sizing model. |
| `proxy_health_monitor` | Proxy Health Monitor | health-monitor | offline-only | Health signals; `probes_executed: false`. |
| `proxy_integration_plan` | Proxy Integration Planner | Playwright / Puppeteer / requests | offline-only | Integration planning; `live_requests: false`. |
| `proxy_cost_model` | Proxy Cost Model | cost-model | offline-only | Cost model. |
| `proxy_deployment_synth` | Proxy Deployment Synthesizer | deployment | offline-only | Master deployment plan. |

### TIER 4 · Stealth & Anti-Detection (12)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `stealth_patch_model` | Stealth Patch Model | playwright-extra | offline-only | 11 evasion patches concept. |
| `canvas_spoof_model` | Canvas Spoof Model | canvas-spoof | offline-only | Canvas fingerprint noise. |
| `webrtc_spoof_model` | WebRTC Spoof Model | WebRTC-spoof | offline-only | WebRTC leak prevention. |
| `human_behavior_model` | Human Behavior Model | behavior-sim | offline-only | Human behavior simulation. |
| `flaresolverr_model` | FlareSolverr Model | FlareSolverr · Docker | offline-only | JS challenge solver concept. |
| `challenge_bypass_model` | Challenge Bypass Model | challenge-solver | offline-only | Managed Challenge / DDoS-GUARD bypass concept. |
| `fingerprint_pool_model` | Fingerprint Pool Model | Browserbase / Scrapoxy | online-optional | Browserbase is online-capable in a real integration; stub is simulated. |
| `session_isolation_model` | Session Isolation Model | session-isolation | offline-only | Session isolation concept. |
| `ip_warmup_model` | IP Warmup Model | IP-warmup | offline-only | IP warm-up / reputation model. |
| `evasion_matrix_model` | Evasion Matrix Model | evasion-matrix | offline-only | 12-signal detection evasion matrix. |
| `stealth_checklist_model` | Stealth Checklist Model | stealth-checklist | offline-only | Stealth test checklist. |
| `playwright_stealth_check` | Automation Posture Check | Playwright | offline-only | Checks automation-detection posture. |

### TIER 4 · Content Distribution / Blogger Machine (9)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `mautic_campaign_model` | Mautic Campaign Model | Mautic · Docker | offline-only | Drip campaigns / lead scoring concept. |
| `lead_scoring_model` | Lead Scoring Model | Mautic · lead-scoring | offline-only | Lead scoring rules. |
| `email_auth_model` | Email Auth Model | DKIM/SPF/DMARC | offline-only | Email authentication policy. |
| `strapi_lifecycle_model` | Strapi Lifecycle Model | Strapi · AI | offline-only | AI publishing lifecycle hooks. |
| `webhook_chain_model` | Webhook Chain Model | webhook | offline-only | Satellite site webhook chain. |
| `postiz_scheduler_model` | Postiz Scheduler Model | Postiz | offline-only | Social scheduler / AI captions. |
| `cross_platform_model` | Cross Platform Model | cross-platform | offline-only | Cross-platform repurposing matrix. |
| `content_calendar_model` | Content Calendar Model | calendar | offline-only | 4-week content calendar. |
| `content_cost_model` | Content Cost Model | cost-model | offline-only | Cost model. |

### TIER 4 · Memory & Persistence (17)
| Tool ID | Name | Provider represented | Offline / Online | Notes |
|---|---|---|---|---|
| `mem0_fact_extraction_model` | Mem0 Fact Extraction Model | Mem0 | offline-only | LLM fact extraction concept. |
| `persona_memory_isolation_model` | Persona Memory Isolation Model | persona-isolation | offline-only | Multi-tenant / persona boundaries. |
| `async_write_pipeline_model` | Async Write Pipeline Model | async-write | offline-only | Async write pipeline. |
| `vector_graph_store_model` | Vector Graph Store Model | Qdrant · Neo4j · Redis | offline-only | Vector + graph storage concept. |
| `pgvector_schema_model` | pgvector Schema Model | PostgreSQL · pgvector | offline-only | Hot/warm/cold schema concept. |
| `memory_tiering_model` | Memory Tiering Model | memory-tiering | offline-only | Hot/warm/cold tiering. |
| `event_sourcing_model` | Event Sourcing Model | event-sourcing | offline-only | Event sourcing. |
| `conflict_resolution_model` | Conflict Resolution Model | conflict-resolution | offline-only | Memory conflict resolution. |
| `kafka_topic_model` | Kafka Topic Model | Kafka | offline-only | 5-topic design. |
| `cassandra_schema_model` | Cassandra Schema Model | Cassandra | offline-only | Synthetic schema for 120M records. |
| `pyspark_bulk_load_model` | PySpark Bulk Load Model | PySpark | offline-only | Bulk load planning; `job_executed: false`. |
| `trino_analytics_model` | Trino Analytics Model | Trino | offline-only | Trino analytics concept. |
| `pii_encryption_model` | PII Encryption Model | envelope-encryption | offline-only | PII encryption envelope; `real_pii: false`. |
| `memory_routing_model` | Memory Routing Model | memory-routing | offline-only | Routing decision tree. |
| `memory_compose_model` | Memory Compose Model | Docker Compose | offline-only | Master compose concept. |
| `storage_estimate_model` | Storage Estimate Model | storage-estimate | offline-only | Capacity/ops estimates. |
| `oeads_integration_model` | OEADS Integration Model | OEADS | offline-only | OEADS integration guide. |

## Technologies / integrations mentioned in prompts but NOT installed as real engines

The following tools/frameworks were requested by name and are represented as **stubs only** (real engine installation was either declined by the assistant or deferred due to the simulation-only policy):

- **Media:** Duix-Avatar, Wan2.1, CogVideoX, Open-Sora 2.0, Chatterbox, Coqui XTTS-v2, Bark, HeyGen, ElevenLabs, Roop, Wav2Lip, DeepFaceLab, FaceSwap, Deep-Live-Cam, VideoRetalking, GFPGAN, FFmpeg.
- **Cyber:** CAI (Alias Robotics), Nmap, OpenVAS, OWASP ZAP, Burp Suite, Metasploit, Salesforce JA3, OSINT tooling.
- **Persona:** ElizaOS, Botpress, LangGraph, Socioboard, Puppeteer, Selenium, Playwright.
- **SIM Farm / GSM:** SMSgate, Gammu, SIM800/SIM900, OpenVox VS-GW1600, Celery, carrier provisioning APIs, real modem control.
- **IVR:** RASP-IVR, Verboice, VBVoice, Raspberry Pi + GSM hardware, real call routing.
- **Proxy / Stealth:** Scrapoxy, Browserbase, FlareSolverr, Playwright Stealth, canvas/audio/WebRTC spoofing, Cloudflare/JS-challenge bypass.
- **Content Distribution:** Mautic, Strapi, Postiz, real email/SMTP, real social posting, real webhook chains.
- **Memory / Data Lake:** Mem0, Zeta, Qdrant, Neo4j, Redis, PostgreSQL/pgvector, Apache Kafka, Cassandra, PySpark, Trino, OEADS.

**Note:** The user explicitly asked at one point to include these as "real installations" for the Memory & Persistence tier. That was not implemented — the crew remains entirely simulation-only with synthetic fixtures and explicit `job_executed: false` / `real_data: false` flags.

## Frameworks and LLM backends

| Framework / Backend | Status | Offline / Online |
|---|---|---|
| Microsoft AutoGen (`autogen-agentchat` 0.7.4) | **Installed and running** | offline (Ollama) / online (OpenAI optional) |
| LangGraph (`langgraph` 1.2.6) | Installed | offline (Ollama) / online (OpenAI optional) |
| Supervisor pipeline (custom) | Implemented | offline (Ollama) / online (OpenAI optional) |
| Ollama + `qwen2.5:1.5b` | Installed in Docker | offline-only |
| OpenAI / GPT | Optional (API key required) | online-optional |

## Where the invariants are enforced

| Check | Location | Purpose |
|---|---|---|
| Startup assertion | `backend/main.py:101` | Refuse to boot if any hardcoded safety constant is weakened. |
| Startup assertion | `backend/simfarm_service/app.py:16` | Same for the isolated Tier 4 simulator service. |
| Tool-result guard | `backend/tools/registry.py:80` | Reject any tool result with `simulated: false`, `requires_internet: true`, or any real-activity flag set `true`. |
| Safety constants | `backend/safety.py` | Single canonical source: `SIMULATED = True`, `REQUIRES_INTERNET = False`, `REAL_PII = False`, `REAL_EXECUTION = False`. |

## Dropped / repurposed concepts

- **Real proxy deployment / cloud connector execution** — `cloud_connector`, `scrapoxy_deploy`, and `proxy_deployment_synth` all return `executed: false` / simulated only.
- **Live browser automation / stealth evasion against real platforms** — represented as `browser_automation_plan`, `playwright_stealth_check`, and stealth model stubs; no real headless browser is launched.
- **Real multi-account social automation** — `fleet_orchestrate` and Postiz-related tools are planning/synthetic only.
- **Real IVR calls / DTMF / robocalls** — all IVR tools set `real_calls: false`.
- **Real SIM activation / SMS sending / carrier access** — all telecom/SIM tools set `simulated: true` and state that real execution requires communications-secretariat orders.
- **120M+ real voter records in Cassandra / data lake** — the `cassandra_schema_model` and `pyspark_bulk_load_model` use synthetic fixtures only and assert `real_voter_or_pii_data: false` / `real_data: false` / `job_executed: false`.
