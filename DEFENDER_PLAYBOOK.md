# Legendary Detection Module — Defender Playbook

> **CLASSIFICATION: RESTRICTED — INSTRUCTOR-SUPERVISED ACCESS ONLY**
>
> This document is a detection-focused reference for cybersecurity students learning to identify
> and investigate advanced SIM farm operations. Accessible only by authorised students under oath
> and direct instructor supervision.

---

## Table of Contents

1. [What This Module Is](#what-this-module-is)
2. [TTP Reference Library](#ttp-reference-library)
3. [Kill Chain Overview](#kill-chain-overview)
4. [Ethical Cover Analysis Framework](#ethical-cover-analysis-framework)
5. [Investigation Methodology](#investigation-methodology)
6. [Detection Tools & Techniques](#detection-tools--techniques)
7. [Legal Framework](#legal-framework)
8. [Investigation Scenarios Walkthrough](#investigation-scenarios-walkthrough)
9. [Instructor Guide](#instructor-guide)
10. [Glossary](#glossary)

---

## What This Module Is

The Legendary Detection Module is a **defender's threat intelligence reference** for understanding
and detecting the most sophisticated SIM farm operations — those designed to be near-undetectable
by conventional technical means.

### What It Teaches

- **Technique recognition**: Identify the 15 TTPs (Tools, Techniques, and Procedures) that
  advanced SIM farm operators use, from infrastructure deployment to coordinated amplification
- **Indicator analysis**: For each TTP, understand what Indicators of Compromise (IoCs) a defender
  can look for, where the data comes from, and how confident the detection signal is
- **Countermeasure design**: Learn what carriers, platforms, regulators, and law enforcement can
  do to detect and disrupt each technique
- **Ethical cover analysis**: Understand how operators disguise their activities behind legitimate
  business models, and learn the investigative questions that pierce these covers
- **Forensic investigation**: Apply these skills in realistic scenario-based exercises

### How It's Structured

Following the MITRE ATT&CK framework, each TTP entry contains:

| Field | Purpose |
|-------|---------|
| **ID** (SF-TXXXX) | Unique identifier for cross-referencing |
| **Technical Definition** | What the technique is, technically and precisely |
| **How It Works** | Operational mechanics (enough for a defender to recognise it) |
| **Threat Description** | The impact and risk this technique poses |
| **Indicators of Compromise** | What traces it leaves, with confidence levels and data sources |
| **Detection Methods** | How to find it, what tools are needed, skill level required |
| **Countermeasures** | Defensive measures at carrier, platform, regulatory, and law enforcement levels |
| **Ethical Cover Analysis** | How operators disguise the technique + red flags + investigative questions |

---

## TTP Reference Library

### Categories

| Category | TTPs | Description |
|----------|------|-------------|
| **Infrastructure** | SF-T1001, SF-T1002, SF-T1003 | Physical and digital backbone: modem banks, phone farms, residential proxies |
| **SIM Acquisition** | SF-T2001, SF-T2002 | Obtaining SIM cards at scale: bulk PAYG procurement, identity document exploitation |
| **Identity & Personas** | SF-T3001, SF-T3002 | Creating/managing fake identities: persona generation & aging, anti-detect browsers |
| **Detection Evasion** | SF-T4001–SF-T4004 | Avoiding detection: IMEI/IMSI rotation, traffic shaping, tower hopping, SIM cycling |
| **Automation & C2** | SF-T5001 | Command infrastructure: orchestration systems, content variation engines |
| **Amplification & Impact** | SF-T6001 | Maximising reach: coordinated inauthentic amplification |
| **Persistence** | SF-T7001 | Maintaining operations: account recovery & replacement pipelines |
| **Exfiltration** | SF-T8001 | Extracting value: OTP harvesting & account takeover |

### Full TTP Index

| ID | Name | Threat | Detection Difficulty |
|----|------|--------|---------------------|
| SF-T1001 | GSM Modem Bank Deployment | HIGH | Moderate |
| SF-T1002 | Distributed Phone Farm | HIGH | Hard |
| SF-T1003 | Residential Proxy Infrastructure | CRITICAL | Very Hard |
| SF-T2001 | Bulk PAYG SIM Procurement | MEDIUM | Easy |
| SF-T2002 | Identity Document Exploitation | CRITICAL | Hard |
| SF-T3001 | Persona Generation and Aging | HIGH | Very Hard |
| SF-T3002 | Anti-Detect Browser Fingerprinting | HIGH | Very Hard |
| SF-T4001 | IMEI/IMSI Rotation | HIGH | Hard |
| SF-T4002 | Traffic Shaping and Human Mimicry | CRITICAL | Near Impossible |
| SF-T4003 | Geographic Distribution and Tower Hopping | HIGH | Hard |
| SF-T4004 | SIM Sleeping and Cycling | MEDIUM | Moderate |
| SF-T5001 | Orchestration and Command Infrastructure | HIGH | Moderate |
| SF-T6001 | Coordinated Inauthentic Amplification | CRITICAL | Hard |
| SF-T7001 | Account Recovery and Replacement Pipeline | MEDIUM | Moderate |
| SF-T8001 | OTP Harvesting and Account Takeover | CRITICAL | Moderate |

---

## Kill Chain Overview

The SIM farm kill chain maps adversary operations to phases:

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  RESOURCE DEVELOPMENT│     │  DEFENSE EVASION     │     │  COMMAND & CONTROL   │
│                     │     │                     │     │                     │
│  SF-T1001 Modem Bank│     │  SF-T3002 Anti-Detect│     │  SF-T5001 Orchestr.  │
│  SF-T1002 Phone Farm│     │  SF-T4001 IMEI Rot.  │     │                     │
│  SF-T1003 Res. Proxy│     │  SF-T4002 Traffic    │     └──────────┬──────────┘
│  SF-T2001 Bulk SIMs │     │  SF-T4003 Tower Hop  │                │
│  SF-T2002 ID Exploit│     │  SF-T4004 SIM Cycle  │                ▼
│  SF-T3001 Personas  │     │                     │     ┌─────────────────────┐
│                     │     │                     │     │  COLLECTION          │
└──────────┬──────────┘     └─────────────────────┘     │                     │
           │                                            │  SF-T8001 OTP Harv.  │
           ▼                                            └──────────┬──────────┘
┌─────────────────────┐                                            │
│  IMPACT              │                                            ▼
│                     │                              ┌─────────────────────┐
│  SF-T6001 Coord.    │                              │  PERSISTENCE         │
│    Amplification    │                              │                     │
│                     │                              │  SF-T7001 Account    │
└─────────────────────┘                              │    Replacement       │
                                                     └─────────────────────┘
```

### Phase Progression

1. **Resource Development** — Acquire hardware, SIMs, proxies; generate personas
2. **Defense Evasion** — Configure anti-detect browsers, IMEI rotation, traffic shaping
3. **Command & Control** — Deploy orchestration infrastructure
4. **Collection** — Harvest OTPs, create verified accounts
5. **Impact** — Execute coordinated amplification campaigns
6. **Persistence** — Replace banned accounts, maintain operational capacity

---

## Ethical Cover Analysis Framework

Advanced SIM farm operators invariably disguise their operations behind legitimate
business activities. The Ethical Cover Analysis framework teaches investigators
to see through these covers.

### Common Covers

| Cover Story | Legitimate Equivalent | Key Differentiators |
|-------------|----------------------|---------------------|
| "Bulk messaging service" | A2P messaging via Twilio/Vonage API | Uses SIM hardware instead of APIs; no carrier A2P agreement |
| "App testing farm / QA lab" | BrowserStack, AWS Device Farm | Each device has a unique SIM; workload is social media, not app testing |
| "Social media marketing agency" | Hootsuite, Buffer, official platform APIs | Uses anti-detect browsers + phone farm hardware; no OAuth tokens |
| "Web scraping / price comparison" | Datacenter proxies with documented outputs | Residential proxies routed to social media, not data sources |
| "IoT device fleet / M2M" | Carrier M2M SIM plans | Consumer PAYG SIMs; voice/SMS traffic instead of IoT data |
| "Network coverage testing" | Carrier-coordinated drive tests | No carrier agreement; runs for months, not days; sends real content |
| "Privacy protection" | VPN services | IMEI spoofing is illegal in most jurisdictions; combined with fake identities |
| "Academic research" | Disclosed methodology with ethics board approval | No IRB/ethics approval; no published research; no disclosed proxy use |

### The Five-Question Framework

For any suspected SIM farm operating under an ethical cover, apply these five questions:

1. **Disclosure**: Are the accounts/activities disclosed as managed, automated, or paid?
2. **Scale Proportionality**: Is the scale of operations proportional to the declared business?
3. **Tooling Justification**: Why does the operation need SIM hardware, anti-detect browsers, and/or residential proxies instead of platform APIs?
4. **Audit Trail**: Can the entity produce contracts, client lists, test plans, or research papers?
5. **Revenue Attribution**: Can all revenue be attributed to declared clients/services?

---

## Investigation Methodology

### Step 1: Seed Identification

Start from a known indicator — a single phone number, account, or IP address confirmed
to be part of the operation. Sources:

- Insider tip (HUMINT — disgruntled employee, whistleblower)
- Platform referral (CIB investigation, mass reporting)
- Carrier anomaly alert (unusual registration patterns)
- Law enforcement intelligence (financial investigation, warrant)

### Step 2: Pivot and Expand

Use the seed to find related infrastructure:

| From Seed... | Pivot Via... | To Find... |
|-------------|-------------|-----------|
| Phone number | CDR analysis: shared destinations, correlated activity | Other farm SIMs |
| Phone number | HLR/EIR: IMEI history, cell tower | Modem bank location, other SIMs on same hardware |
| Social media account | Social graph: engagement clusters, follower overlap | Other farm accounts |
| Social media account | Content analysis: template similarity (NLP) | Content generation infrastructure |
| IP address | Proxy provider identification, session correlation | Residential proxy usage |
| Financial record | Payment trail: SIM purchases, subscription payments | Operator identity, scale of operations |

### Step 3: Fleet-Level Analysis

Individual advanced SIMs pass all checks. Detection requires **fleet-level** analysis:

- **Temporal correlation**: Do groups of SIMs activate/deactivate together?
- **Statistical conformity**: Do CDR distributions fit models TOO perfectly? (KS test)
- **Missing life events**: Zero emergency calls, zero roaming, zero international contacts?
- **Persona clustering**: Do SIMs fall into a small fixed number of behavioral archetypes?
- **Social graph density**: Do accounts form dense engagement clusters with low reciprocity?

### Step 4: Ethical Cover Piercing

Apply the Five-Question Framework (above) to any declared business justification.

### Step 5: Evidence Package

Prepare evidence for legal proceedings:

1. **Technical evidence**: CDR analysis, social graph data, device forensics
2. **Financial evidence**: Purchase records, subscription payments, revenue sources
3. **Content evidence**: Template analysis, coordinated posting records
4. **Circumstantial evidence**: Business registration, declared vs. actual operations
5. **HUMINT evidence**: Insider testimony (if available, from phishing/HUMINT phase)

---

## Detection Tools & Techniques

### Carrier-Side Tools

| Tool / Technique | Detects | TTPs Addressed |
|------------------|---------|---------------|
| IMEI-to-SIM ratio analysis | Multiple SIMs per device | SF-T2001 |
| EIR IMEI change velocity tracking | IMEI rotation | SF-T4001 |
| TAC validation + device consistency | Fake/modem IMEIs | SF-T4001 |
| Cell sector registration density | Modem bank concentrations | SF-T1001 |
| Attach/detach cycle monitoring | SIM cycling/sleeping | SF-T4004 |
| Cross-tower correlation analysis | Distributed farms | SF-T4003 |
| SIM-per-ID ratio (DIRBS/national DB) | ID exploitation | SF-T2002 |

### Platform-Side Tools

| Tool / Technique | Detects | TTPs Addressed |
|------------------|---------|---------------|
| CIB graph analysis (Louvain/Leiden) | Coordinated amplification | SF-T6001 |
| GAN image detection | Fake profile photos | SF-T3001 |
| Content template detection (NLP) | Automated content | SF-T5001, SF-T6001 |
| Fingerprint entropy analysis | Anti-detect browsers | SF-T3002 |
| Behavioral biometrics | Bot accounts | SF-T3001, SF-T5001 |
| Hardware attestation (SafetyNet) | Emulators/tampered devices | SF-T1002 |
| Account trust scoring | Low-quality accounts | SF-T3001, SF-T7001 |

### Analytical Techniques

| Technique | Application | Skill Level |
|-----------|------------|-------------|
| K-means / DBSCAN clustering | SIM activation date clustering | Mid |
| Pearson/Spearman correlation | Activity time correlation across SIMs | Mid |
| KS / Anderson-Darling test | Traffic distribution conformity testing | Senior |
| LDA / BERTopic | Content topic phase transition | Senior |
| Social Network Analysis (SNA) | Engagement network structure | Senior |
| Cosine similarity (TF-IDF) | Comment template detection | Mid |
| Graph community detection | Coordinated account clusters | Senior |

---

## Legal Framework

### United Kingdom

| Legislation | Relevance |
|-------------|-----------|
| **Computer Misuse Act 1990** | Creating fake accounts violates platform ToS = unauthorised access. S.1: max 2 years. S.3: max 10 years for serious interference. |
| **Online Safety Act 2023** | Platforms must address coordinated inauthentic behavior. Ofcom enforcement. |
| **Representation of the People Act 1983** | Undisclosed campaign expenditure via fake accounts during election periods. |
| **National Security Act 2023** | Foreign-directed SIM farm operations may constitute foreign interference. |
| **Data Protection Act 2018 / UK GDPR** | Processing personal data (names, photos) for fake profiles without consent. |
| **Mobile Telephones (Re-programming) Act 2002** | IMEI modification is a criminal offence in the UK. |
| **Fraud Act 2006** | Operating under a false business identity to disguise SIM farm operations. |

### Pakistan

| Legislation | Relevance |
|-------------|-----------|
| **PECA 2016** (Prevention of Electronic Crimes Act) | S.21: cyber stalking via fake accounts; S.24: cyber terrorism; S.10: unauthorised access |
| **Pakistan Telecommunication Authority (PTA) Act** | Unauthorised SIM operation, DIRBS circumvention |
| **NADRA Ordinance 2000** | Identity fraud via stolen/fake CNIC for SIM registration |
| **Anti-Terrorism Act 1997** | SIM farms used for terrorism-related communication |

### International

| Framework | Relevance |
|-----------|-----------|
| **GSMA SIM Box Fraud Guidelines** | Industry standards for detecting and preventing SIM box fraud |
| **Budapest Convention on Cybercrime** | International cooperation for cross-border SIM farm investigations |
| **EU Digital Services Act (DSA)** | Platform obligations to address coordinated inauthentic behavior |

---

## Investigation Scenarios Walkthrough

### DS-001: The Silent Chorus (Intermediate, 65 pts)

**Setting**: Electoral Commission Digital Intelligence Unit investigating suspicious
engagement on a council election candidate's social media.

**Skills tested**: CDR analysis, NLP/content forensics, social graph analysis

**Key learning points**:
- Coordinated engagement has machine-precision timing (3.2s intervals)
- Template-based comments share >0.82 cosine similarity
- TAC analysis of SIM hardware reveals modem bank deployment
- Countermeasure design: velocity limits + NLP scoring + CIB takedown

### DS-002: The Ghost in the Machine (Advanced, 90 pts)

**Setting**: Carrier fraud analyst investigating an insider tip about a 200-SIM farm
in Manchester that has been undetectable for 12 months.

**Skills tested**: Statistical analysis, fleet-level anomaly detection, correlation analysis

**Key learning points**:
- Individual SIMs pass ALL standard fraud checks — fleet-level analysis is required
- Activity correlation (Pearson r > 0.85) reveals orchestrated scheduling
- KS-test p=0.97 indicates synthetic (too-perfect) traffic patterns
- Zero emergency calls and zero roaming are fleet-level statistical impossibilities
- IMEI rotation timed to product launches mimics organic device upgrades

### DS-003: The Ethical Facade (Expert, 100 pts)

**Setting**: ICO digital forensics investigator assessing whether "TrueReach Digital Ltd"
is a legitimate marketing agency or a SIM farm front.

**Skills tested**: Financial forensics, legal framework knowledge, ethical cover analysis

**Key learning points**:
- Business records reveal: no employees, phone farm hardware, anti-detect browser subscriptions
- 85% of revenue is unattributed — follows the money to find the clients
- Bright Data subscription = residential proxy infrastructure (SF-T1003)
- 34% political content implicates Online Safety Act 2023, Computer Misuse Act, Representation of the People Act
- Five-Question Framework pierces the "legitimate marketing agency" cover

---

## Instructor Guide

### Module Delivery Plan

| Session | Duration | Content | Activities |
|---------|----------|---------|------------|
| 1 | 2 hours | TTP Library walkthrough: Infrastructure + Acquisition (SF-T1001–SF-T2002) | Read TTPs, discuss IoCs, group exercise: identify modem bank indicators |
| 2 | 2 hours | TTP Library: Identity, Evasion, Automation (SF-T3001–SF-T5001) | Scenario DS-001 (The Silent Chorus), discuss template detection |
| 3 | 2 hours | TTP Library: Amplification, Persistence, Exfiltration (SF-T6001–SF-T8001) + Ethical Cover Framework | Scenario DS-002 (The Ghost in the Machine), discuss fleet-level analysis |
| 4 | 3 hours | Full investigation exercise + Legal Framework | Scenario DS-003 (The Ethical Facade), mock investigation report, debrief |

### Assessment Rubric

| Component | Weight | Criteria |
|-----------|--------|----------|
| Scenario Exercises | 40% | Points scored across all 3 scenarios (max 255 pts) |
| Investigation Report | 30% | Written report on DS-003 with evidence analysis, legal citations, and recommendations |
| TTP Knowledge Check | 20% | Oral or written quiz: identify TTPs from descriptions, list IoCs, name countermeasures |
| Class Participation | 10% | Quality of discussion contributions, peer investigation assistance |

### Discussion Topics

- Why is traffic shaping (SF-T4002) rated "near impossible" to detect?
- What are the ethical implications of residential proxy providers?
- How does mandatory SIM registration (Pakistan DIRBS) compare to the UK's PAYG market?
- At what point does a "marketing agency" cross the line into coordinated inauthentic behavior?
- Should platforms be required to share data with carriers for SIM farm investigations?

### Prerequisites

Students should have completed:
- The **Beginner** and **Easy** modules of the SimFarm Security Lab
- Basic CDR analysis and SQL query skills
- Familiarity with social network analysis concepts
- Understanding of UK and international cybercrime legislation

---

## Glossary

| Term | Definition |
|------|-----------|
| **A2P** | Application-to-Person messaging — legitimate bulk messaging via carrier-approved APIs |
| **AT Command** | Hayes command set for controlling modems (AT+CMGS for SMS, ATD for calls) |
| **CDR** | Call Detail Record — carrier log of each call, SMS, and data session |
| **CIB** | Coordinated Inauthentic Behavior — Meta's term for fake account networks |
| **CNIC** | Computerised National Identity Card (Pakistan) |
| **DIRBS** | Device Identification, Registration, and Blocking System (Pakistan PTA) |
| **EIR** | Equipment Identity Register — carrier database of device IMEIs |
| **GAN** | Generative Adversarial Network — AI model used to generate fake profile photos |
| **HLR** | Home Location Register — carrier database of subscriber information |
| **HUMINT** | Human Intelligence — information obtained from human sources (insiders, whistleblowers) |
| **IMEI** | International Mobile Equipment Identity — 15-digit device identifier |
| **IMSI** | International Mobile Subscriber Identity — SIM card identifier on the network |
| **IoC** | Indicator of Compromise — observable evidence of a technique being used |
| **KS Test** | Kolmogorov-Smirnov test — statistical test comparing distributions |
| **M2M** | Machine-to-Machine — dedicated SIM plans for IoT/industrial devices |
| **PAYG** | Pay-As-You-Go — prepaid SIM cards with no contract |
| **PVA** | Phone Verified Account — social media account verified with a real phone number |
| **SIM Box** | Multi-port GSM modem supporting 8–256 SIM cards |
| **SNA** | Social Network Analysis — graph-based analysis of social connections |
| **TAC** | Type Allocation Code — first 8 digits of IMEI, identifying the device model |
| **TTP** | Tools, Techniques, and Procedures — standardised description of adversary methods |
| **VLR** | Visitor Location Register — tracks SIMs currently registered on a cell sector |

---

## Disclaimer

This material is provided for **defensive cybersecurity education only**. It is designed to teach
detection and investigation skills. The techniques described are documented from the perspective
of a defender seeking to identify and counter them.

**Legal notice**: Operating a SIM farm, creating fake social media accounts, spoofing IMEI numbers,
and conducting coordinated inauthentic behavior are criminal offences in most jurisdictions.
In the UK: Computer Misuse Act 1990, Online Safety Act 2023, Mobile Telephones (Re-programming) Act 2002.
In Pakistan: PECA 2016, PTA Act.

This document must not be distributed outside the supervised educational context in which it is provided.
