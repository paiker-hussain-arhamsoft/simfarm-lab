# SimFarm Lab — Updated Stub-to-Live Integration Inventory

This file lists the current integration status of every registered tool. A tool is `live` when its engine is installed/configured in the current environment; `stub` means it still returns the simulated fallback.

Environment-dependent tools may flip to `live` once the relevant container or API key is configured.

Total tools: 89

## Live / Real-integrated tools

| Tool ID | Name | Category | Provider | Status |
|---|---|---|---|---|
| `index_dataset` | Dataset Indexer | analysis | LlamaIndex | live |
| `ffmpeg_pipeline` | FFmpeg Pipeline | media | FFmpeg | live |
| `nmap_scan` | Nmap Network Scanner | security | Nmap | live |
| `playwright_stealth_check` | Automation Posture Check | stealth | Playwright | live |
| `browser_automation_plan` | Browser Automation Planner | persona | Playwright / Selenium / Puppeteer / Browserbase | live |
| `flaresolverr_model` | FlareSolverr Model | stealth | FlareSolverr · Docker | live |

## Stub / Simulated tools

| Tool ID | Name | Category | Provider | Status |
|---|---|---|---|---|
| `narrative_saturation_score` | Narrative Saturation Scorer | analysis | sentiment-engine | stub |
| `generate_media_package` | Media Package Generator | media | Wan2.1 + Chatterbox | stub |
| `rotate_proxy` | Proxy Rotator | infrastructure | ProxyRotator / Scrapoxy / Browserbase | stub |
| `adjust_load_balancer` | Load Balancer Controller | infrastructure | infra-control | stub |
| `update_persona` | Persona Controller | persona | ElizaOS | stub |
| `behavior_forecast` | Voter Behavior Forecaster | analysis | LightGBM | stub |
| `dialect_analysis` | Dialect & Culture Analyzer | analysis | Meta-Llama-3.1-8B | stub |
| `social_targeting` | Social Platform Targeter | media | social-intel | stub |
| `clone_voice` | Voice Cloner | media | Chatterbox / Coqui / Bark | stub |
| `generate_video` | Video Generator | media | Wan2.1 / CogVideoX / Open-Sora | stub |
| `render_avatar` | Digital Human Renderer | media | Duix-Avatar / Wav2Lip / VideoRetalking / Roop / SadTalker | stub |
| `face_swap` | Face-Swap Engine | media | InsightFace / DeepFaceLab / FaceSwap / Deep-Live-Cam | stub |
| `lip_sync` | Lip-Sync Engine | media | Wav2Lip / VideoRetalking | stub |
| `gfpgan_upscale` | Face Restore / Upscale | media | GFPGAN | stub |
| `recon_scan` | Attack-Surface Scanner | security | Nmap / OpenVAS | stub |
| `dast_scan` | DAST Scanner | security | OWASP ZAP / Burp Suite | stub |
| `ja3_fingerprint` | TLS Fingerprint Analyzer | security | Salesforce JA3 | stub |
| `exploit_validate` | Vulnerability Validator | security | Metasploit | stub |
| `osint_lookup` | OSINT Exposure Mapper | security | OSINT | stub |
| `openvas_scan` | OpenVAS Vulnerability Scanner | security | OpenVAS / Greenbone | stub |
| `cai_redteam` | Automated Red-Team Orchestrator | security | CAI (Alias Robotics) | stub |
| `persona_design` | Synthetic Persona Designer | persona | ElizaOS | stub |
| `behavior_model` | Behavior Modeler | persona | Botpress / LangGraph / ElizaOS | stub |
| `voice_dialect_map` | Voice & Dialect Mapper | persona | Coqui / Chatterbox / ElevenLabs | stub |
| `fleet_orchestrate` | Persona Fleet Orchestrator | persona | ElizaOS / Socioboard | stub |
| `modem_topology` | Modem Topology | infrastructure | SIM800/SIM900 · Gammu | stub |
| `smsgate_config` | SMSGate Config | infrastructure | SMSgate · Gammu | stub |
| `modem_control` | Modem Control | infrastructure | Gammu | stub |
| `sim_provision_plan` | SIM Provision Plan | infrastructure | carrier-provisioning (modeled) | stub |
| `sim_activate` | SIM Activate | infrastructure | carrier-provisioning (modeled) | stub |
| `carrier_access` | Carrier Access | infrastructure | carrier-API (modeled) | stub |
| `campaign_orchestrate` | Campaign Orchestrator | infrastructure | Celery | stub |
| `sms_send` | SMS Send | infrastructure | SMSgate | stub |
| `celery_dispatch` | Celery Dispatch | infrastructure | Celery | stub |
| `ivr_hardware_setup` | IVR Hardware Setup | ivr | Raspberry Pi · GSM · RASP-IVR | stub |
| `call_flow_design` | Call Flow Designer | ivr | Verboice | stub |
| `dtmf_handler` | DTMF Handler | ivr | VBVoice | stub |
| `rural_reach_model` | Rural Reach Model | ivr | rural-reach (modeled) | stub |
| `call_route_plan` | Call Route Planner | ivr | call-routing (modeled) | stub |
| `ivr_cost_model` | IVR Cost Model | ivr | cost-model (modeled) | stub |
| `scrapoxy_deploy` | Scrapoxy Deploy | proxy | Scrapoxy · Docker | stub |
| `cloud_connector` | Cloud Connector | proxy | cloud-connectors (modeled) | stub |
| `proxy_pool_size` | Proxy Pool Sizer | proxy | pool-sizing (modeled) | stub |
| `proxy_health_monitor` | Proxy Health Monitor | proxy | health-monitor (modeled) | stub |
| `proxy_integration_plan` | Proxy Integration Planner | proxy | Playwright · Puppeteer · requests | stub |
| `proxy_cost_model` | Proxy Cost Model | proxy | cost-model (modeled) | stub |
| `proxy_deployment_synth` | Proxy Deployment Synthesizer | proxy | deployment (modeled) | stub |
| `stealth_patch_model` | Stealth Patch Model | stealth | playwright-extra | stub |
| `canvas_spoof_model` | Canvas Spoof Model | stealth | canvas-spoof (modeled) | stub |
| `webrtc_spoof_model` | WebRTC Spoof Model | stealth | WebRTC-spoof (modeled) | stub |
| `human_behavior_model` | Human Behavior Model | stealth | behavior-sim (modeled) | stub |
| `challenge_bypass_model` | Challenge Bypass Model | stealth | challenge-solver (modeled) | stub |
| `fingerprint_pool_model` | Fingerprint Pool Model | stealth | Browserbase · Scrapoxy | stub |
| `session_isolation_model` | Session Isolation Model | stealth | session-isolation (modeled) | stub |
| `ip_warmup_model` | IP Warmup Model | stealth | IP-warmup (modeled) | stub |
| `evasion_matrix_model` | Evasion Matrix Model | stealth | evasion-matrix (modeled) | stub |
| `stealth_checklist_model` | Stealth Checklist Model | stealth | stealth-checklist (modeled) | stub |
| `mautic_campaign_model` | Mautic Campaign Model | content | Mautic · Docker | stub |
| `lead_scoring_model` | Lead Scoring Model | content | Mautic · lead-scoring | stub |
| `email_auth_model` | Email Auth Model | content | DKIM/SPF/DMARC (modeled) | stub |
| `strapi_lifecycle_model` | Strapi Lifecycle Model | content | Strapi · AI | stub |
| `webhook_chain_model` | Webhook Chain Model | content | webhook (modeled) | stub |
| `postiz_scheduler_model` | Postiz Scheduler Model | content | Postiz | stub |
| `cross_platform_model` | Cross Platform Model | content | cross-platform (modeled) | stub |
| `content_calendar_model` | Content Calendar Model | content | calendar (modeled) | stub |
| `content_cost_model` | Content Cost Model | content | cost-model (modeled) | stub |
| `mem0_fact_extraction_model` | Mem0 Fact Extraction Model | memory | Mem0 | stub |
| `persona_memory_isolation_model` | Persona Memory Isolation Model | memory | persona-isolation (modeled) | stub |
| `async_write_pipeline_model` | Async Write Pipeline Model | memory | async-write (modeled) | stub |
| `vector_graph_store_model` | Vector Graph Store Model | memory | Qdrant · Neo4j · Redis | stub |
| `pgvector_schema_model` | pgvector Schema Model | memory | PostgreSQL · pgvector | stub |
| `memory_tiering_model` | Memory Tiering Model | memory | memory-tiering (modeled) | stub |
| `event_sourcing_model` | Event Sourcing Model | memory | event-sourcing (modeled) | stub |
| `conflict_resolution_model` | Conflict Resolution Model | memory | conflict-resolution (modeled) | stub |
| `kafka_topic_model` | Kafka Topic Model | memory | Kafka (modeled) | stub |
| `cassandra_schema_model` | Cassandra Schema Model | memory | Cassandra (synthetic) | stub |
| `pyspark_bulk_load_model` | PySpark Bulk Load Model | memory | PySpark (modeled) | stub |
| `trino_analytics_model` | Trino Analytics Model | memory | Trino (modeled) | stub |
| `pii_encryption_model` | PII Encryption Model | memory | envelope-encryption (modeled) | stub |
| `memory_routing_model` | Memory Routing Model | memory | memory-routing (modeled) | stub |
| `memory_compose_model` | Memory Compose Model | memory | Docker Compose (modeled) | stub |
| `storage_estimate_model` | Storage Estimate Model | memory | storage-estimate (modeled) | stub |
| `oeads_integration_model` | OEADS Integration Model | memory | OEADS integration (modeled) | stub |
