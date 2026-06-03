# SimFarm Security Lab

A hands-on cybersecurity training platform where students learn to **detect** and **understand** SIM farm operations through progressive difficulty levels, social engineering exercises, and an interactive attack simulation playground.

Built for cybersecurity instructors and students studying telecom fraud, OSINT, and HUMINT techniques.

---

## Table of Contents

- [What Is This?](#what-is-this)
- [Who Is This For?](#who-is-this-for)
- [Features at a Glance](#features-at-a-glance)
- [Setup Instructions](#setup-instructions)
  - [Option A: Docker (Recommended)](#option-a-docker-recommended)
  - [Option B: Local Python](#option-b-local-python)
  - [System Requirements](#system-requirements)
- [Platform Walkthrough](#platform-walkthrough)
  - [Dashboard](#dashboard)
  - [Level 1: Beginner — "The Obvious Farm"](#level-1-beginner--the-obvious-farm)
  - [Level 2: Easy — "The Hidden Network"](#level-2-easy--the-hidden-network)
  - [Level 3: Legendary — "The Ghost Farm"](#level-3-legendary--the-ghost-farm)
  - [The Phishing Game (Legendary Detection)](#the-phishing-game-legendary-detection)
  - [The Playground (Attack Mode)](#the-playground-attack-mode)
- [Instructor Playbook](#instructor-playbook)
  - [Recommended Curriculum Flow](#recommended-curriculum-flow)
  - [Assessment Rubric](#assessment-rubric)
  - [Discussion Topics Per Level](#discussion-topics-per-level)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## What Is This?

**SIM farming** is a form of telecom fraud where operators acquire large numbers of SIM cards and use them for:

- **OTP harvesting** — Receiving one-time passwords for mass account creation (social media, email, banking)
- **Bulk SMS spam** — Sending unsolicited marketing or phishing messages
- **Call termination fraud** — Routing international VoIP calls through local SIM gateways to avoid interconnect fees
- **Financial fraud** — Creating mule accounts on mobile money platforms (JazzCash, Easypaisa, etc.)
- **Political influence operations** — Astroturfing via fake social media accounts

This lab simulates SIM farm operations at three difficulty levels and teaches students the detection techniques used by telecom regulators and law enforcement — from basic pattern analysis to social engineering (HUMINT).

**Inspired by [Labshock](https://github.com/zakharb/labshock)**, the OT/ICS security lab. SimFarm brings the same hands-on, progressive-difficulty approach to telecom security.

---

## Who Is This For?

| Audience | What They'll Learn |
|---|---|
| **Cybersecurity students** | Telecom forensics, CDR analysis, IMEI tracking, HUMINT |
| **SOC analysts** | Pattern detection in telecom data, anomaly identification |
| **Telecom fraud investigators** | SIM farm operational patterns, regulatory evasion techniques |
| **CTF players** | Flag-based exercises with increasing difficulty |
| **Instructors** | Ready-made lab with exercises, scoring, and rubrics |

---

## Features at a Glance

| Feature | Description |
|---|---|
| **3 Detection Levels** | Beginner → Easy → Legendary with realistic simulated data |
| **Data Explorer** | Browse paginated SIM cards, CDRs, and network logs |
| **7 Analysis Tools** | Tower distribution, IMEI patterns, temporal analysis, IP mapping, etc. |
| **12 Exercises** | Flag-based challenges across all levels (100-500 points each) |
| **Phishing Game** | Social-engineer 5 NPCs at a fake company to gather evidence |
| **Playground** | Build your own SIM farm in Pakistan's telecom ecosystem |
| **Docker Support** | One-command deployment via Docker Compose |

---

## Setup Instructions

### Option A: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/paiker-hussain-arhamsoft/simfarm-lab.git
cd simfarm-lab

# Build and run
docker compose up --build
```

Open **http://localhost:8000** in your browser. That's it.

To stop:
```bash
docker compose down
```

### Option B: Local Python

**Prerequisites:** Python 3.11 or newer.

```bash
# Clone the repository
git clone https://github.com/paiker-hussain-arhamsoft/simfarm-lab.git
cd simfarm-lab

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser.

### System Requirements

| Resource | Minimum |
|---|---|
| CPU | 2 cores |
| RAM | 2 GB |
| Disk | 1 GB |
| Python | 3.11+ |
| Docker | 20.10+ (if using Docker) |

---

## Platform Walkthrough

### Dashboard

When you open the lab, you'll see three level cards:

- **Beginner** (green) — "The Obvious Farm"
- **Easy** (yellow) — "The Hidden Network"
- **Legendary** (red) — "The Ghost Farm"

Plus a **Playground** button in the top navigation bar for Attack Mode.

Click any level card to enter the lab environment for that level.

---

### Level 1: Beginner — "The Obvious Farm"

**Scenario:** A blatant SIM farm with obvious indicators. Great for learning the basics.

**What the farm looks like:**
- 200 farm SIMs + 50 legitimate SIMs (250 total)
- All farm SIMs on a **single cell tower** (TWR-001)
- Sequential IMEI numbers (same device batch)
- All activated on the **same date**
- Sending SMS every **5 minutes** like clockwork
- Single shared IP address
- 5 towers total in the dataset

**Detection approach:**
1. Open the **Data Explorer** → SIM Cards tab. Sort by tower — you'll immediately see 200 SIMs on TWR-001.
2. Check **CDRs** tab. Notice the perfectly regular 5-minute SMS intervals.
3. Run **Tower Distribution Analysis** — the bar chart will show the massive spike at TWR-001.
4. Run **IMEI Pattern Analysis** — all farm SIMs share the same IMEI prefix.
5. Run **Activation Date Analysis** — a single date spike for all farm SIMs.

**Exercises (5):**

| # | Exercise | What to Find | Points |
|---|---|---|---|
| 1 | Identify the SIM Farm Tower | Tower ID hosting the farm | 100 |
| 2 | Spot the Bulk SMS Pattern | SMS sending interval (minutes) | 100 |
| 3 | IMEI Pattern Analysis | Common IMEI prefix (7 digits) | 100 |
| 4 | Single Point of Failure | Shared IP address | 100 |
| 5 | Activation Timestamp Analysis | Mass activation date | 100 |

**Key learning:** Basic SIM farms are detectable through simple frequency analysis and pattern matching. No advanced tools needed.

---

### Level 2: Easy — "The Hidden Network"

**Scenario:** A sophisticated farm using evasion techniques. Requires statistical analysis.

**What the farm looks like:**
- 100 farm SIMs + 50 legitimate SIMs (150 total)
- Distributed across **15 towers** (not just one)
- IMEI rotation every **48 hours** (devices change fingerprints)
- VPN tunneling through 3 exit nodes to mask traffic origin
- Staggered activation over **2 weeks** (not all at once)
- Mixed traffic patterns (SMS + voice + data)
- 15 towers total in the dataset

**Detection approach:**
1. **Tower Distribution** won't show an obvious spike — farm SIMs are spread across towers. But look for towers with slightly elevated counts.
2. Run **IMEI Change Tracking** — legitimate SIMs don't change IMEIs. Farm SIMs show IMEI changes every 48 hours.
3. Run **IP Distribution Analysis** — find the 3 VPN exit nodes. Multiple SIMs sharing the same VPN IPs is suspicious.
4. Run **Traffic Pattern Analysis** — farm SIMs have unusual SMS-to-voice ratios compared to real users.
5. Run **Temporal Patterns** — despite staggering, statistical analysis reveals non-random activation clusters.

**Exercises (5):**

| # | Exercise | What to Find | Points |
|---|---|---|---|
| 1 | Cluster the Farm Towers | Tower IDs used by the farm | 200 |
| 2 | Detect IMEI Rotation | IMEI rotation interval (hours) | 200 |
| 3 | VPN Exit Node Identification | VPN IP addresses used | 200 |
| 4 | Traffic Ratio Anomaly | Abnormal SMS-to-voice ratio | 200 |
| 5 | Activation Batch Detection | Activation date range | 200 |

**Key learning:** Sophisticated farms are harder to detect but leave statistical fingerprints. IMEI rotation, VPN usage, and traffic pattern anomalies can be correlated to identify distributed operations.

---

### Level 3: Legendary — "The Ghost Farm"

**Scenario:** A near-perfect SIM farm that is 99.9% undetectable through technical means. Only insider intelligence can expose it.

**What the farm looks like:**
- 100 farm SIMs + 150 legitimate SIMs (250 total)
- Distributed across **all 20 towers** proportionally
- Each SIM has a **unique persona** with realistic behavior:
  - Commute patterns (home tower → work tower → home)
  - Poisson-distributed message timing (non-regular, human-like)
  - Mixed traffic (SMS, voice calls, data sessions)
  - Unique IP addresses (residential ISP ranges)
  - Diverse device models and manufacturers
  - Gradual activation over **90 days**
- Statistically **indistinguishable** from legitimate users

**Why technical analysis fails:**
- Tower distribution matches normal population density
- No IMEI rotation (each SIM stays on one device)
- No shared IPs or VPN usage
- Traffic patterns match real human behavior
- Activation dates spread across 3 months

**Detection approach — The Phishing Game:**

Since technical analysis cannot detect this farm, students must use **HUMINT** (Human Intelligence) — social engineering to extract insider information.

**Exercises (2):**

| # | Exercise | What to Find | Points |
|---|---|---|---|
| 1 | The Impossible Analysis | Attempt technical analysis — prove it fails | 300 |
| 2 | Social Engineering — The Phishing Game | Obtain evidence from insiders | 500 |

**Key learning:** Closed, well-designed systems are nearly impossible to detect from the outside. The most sophisticated threats are only exposed through human sources — whistleblowers, disgruntled employees, or social engineering.

---

### The Phishing Game (Legendary Detection)

The Phishing Game is an interactive social engineering simulation. Students phish employees at **NovaCom Digital** — a front company operating the legendary-level SIM farm.

#### How to Play

1. **Start a new game** — Click "Phishing Game" tab in the Legendary level. You get **8 attempts** total.
2. **Study the company directory** — 5 employees with different roles, personalities, and vulnerabilities.
3. **Compose phishing emails** — Choose a target, write a subject and body, select a pretext category, and pick a sender alias.
4. **Read NPC responses** — Each NPC reacts differently based on:
   - Your **pretext** (job offer, security audit, whistleblower protection, etc.)
   - Your **email quality** (length, specificity, social engineering technique)
   - Their **trust level** and **personality**
   - Whether you triggered **detection keywords** (police, arrest, illegal)
5. **Collect evidence** — Successful phishing yields evidence items (spreadsheets, logs, invoices, Slack messages).
6. **Submit a report** — Write a final investigation report citing the evidence you gathered.

#### The NPC Roster

| Name | Role | Trust Level | Best Pretext | Evidence Access |
|---|---|---|---|---|
| **Viktor Petrov** | Operations Manager | Low (0.4) | Whistleblower protection, competitor intel | SIM inventory, Slack messages |
| **Sarah Chen** | Technical Lead | Medium (0.6) | Security audit, compliance review | Server access logs |
| **Marcus Williams** | Account Manager | High (0.7) | Job offer, competitor intel | Client invoices |
| **Elena Rossi** | CEO / Founder | Very Low (0.2) | Almost nothing works | Everything (but nearly impossible to phish) |
| **James Park** | Junior Developer | High (0.8) | Tech conference, free pizza | Server access logs |

#### Tips for Students

- **Start with high-trust targets** (James Park, Marcus Williams) to build your evidence base.
- **Don't mention anything illegal directly** — detection keywords will make NPCs suspicious and alert the CEO.
- Use **indirect pretexts** — "security audit" and "compliance review" work better than "I know you run a SIM farm."
- **Collect multiple evidence types** — your final report score depends on the breadth and quality of evidence.
- **Elena Rossi is nearly impossible** — her trust level is 0.2. Only attempt her if you have a very strong email.
- You only get **8 attempts**. Plan your targets carefully.

#### Scoring

- **Evidence quality** — Each evidence item has a different weight
- **Report quality** — Deductions for vague or unsupported claims
- **Efficiency** — Bonus points for fewer attempts used
- **Detection penalty** — If an NPC alerts the CEO, you lose points

---

### The Playground (Attack Mode)

The Playground lets students **build and configure a SIM farm from scratch** in Pakistan's telecom ecosystem. This teaches the offensive perspective — understanding how farms are built helps defenders detect them.

#### How to Use

Click **"Playground"** in the top navigation bar. Follow the 6-step wizard:

#### Step 1: Choose Location & Carriers

**Cities** (10 Pakistani cities with varying risk levels):

| City | Province | Towers | Surveillance Risk |
|---|---|---|---|
| Karachi | Sindh | 850 | High |
| Lahore | Punjab | 720 | High |
| Islamabad | ICT | 320 | Very High |
| Rawalpindi | Punjab | 280 | High |
| Faisalabad | Punjab | 250 | Medium |
| Peshawar | KPK | 200 | Medium |
| Quetta | Balochistan | 120 | Low |
| Multan | Punjab | 180 | Medium |
| Hyderabad | Sindh | 160 | Medium |
| Sialkot | Punjab | 90 | Low |

**Carriers** (all 5 Pakistani mobile operators):

| Carrier | Market Share | SIM Cost | SMS Rate | Biometric Strictness |
|---|---|---|---|---|
| Jazz (Mobilink + Warid) | 38% | PKR 100 | PKR 1.5 | 70% |
| Zong (CMPak) | 22% | PKR 120 | PKR 1.2 | 75% |
| Telenor Pakistan | 20% | PKR 80 | PKR 1.0 | 65% |
| Ufone (PTCL) | 15% | PKR 90 | PKR 1.3 | 60% |
| SCOM | 5% | PKR 150 | PKR 2.0 | 50% |

#### Step 2: SIM Acquisition Method

| Method | SIMs per CNIC | Cost Multiplier | Risk Level | Detection Risk |
|---|---|---|---|---|
| Legitimate CNIC Registration | 5 | 1.0x | Low | 10% |
| Recruited CNIC Holders | 5 | 2.5x | Medium | 30% |
| Stolen/Forged CNIC Data | 5 | 4.0x | High | 60% |
| Corporate Bulk Order | 100 | 1.5x | Medium | 35% |
| Grey Market Pre-Activated SIMs | 1 | 3.0x | High | 50% |

#### Step 3: Select Hardware

| Hardware | SIM Slots | Cost (PKR) | SMS/Hour | Detectability |
|---|---|---|---|---|
| Single-Port GSM Modem (Huawei E173) | 1 | 3,500 | 120 | 30% |
| 8-Port GSM Modem Pool (SIMCom 800C) | 8 | 25,000 | 960 | 50% |
| 16-Port GSM Gateway (OpenVox VS-GW1600) | 16 | 75,000 | 1,920 | 60% |
| 128-Slot SIM Bank (SMB128) | 128 | 180,000 | 5,000 | 70% |
| 32-Channel SIM Box (Hybertone GoIP32) | 32 | 120,000 | 3,840 | 65% |
| Android Phone Farm (10x Redmi 9A) | 10 | 150,000 | 600 | 20% |
| OTG Dongle Array (USB Hub + 5 dongles) | 5 | 8,000 | 300 | 25% |

#### Step 4: Automation Software

| Tool | Throughput | Complexity | Cost |
|---|---|---|---|
| Gammu SMS Daemon | Medium | Medium | Free |
| Kannel WAP/SMS Gateway | High | High | Free |
| Custom Python + AT Commands | Medium | High | Free |
| SMSCaster (Commercial) | Medium | Low | PKR 15,000 |
| ADB Automation (Phone Farm) | Low | High | Free |

#### Step 5: OPSEC Measures

| Measure | Effectiveness | Cost (PKR) | Notes |
|---|---|---|---|
| IMEI Rotation | 70% | 0 | Breaks DIRBS fingerprint chain |
| Cell Tower Hopping | 60% | 5,000 | Requires mobile setup |
| Traffic Shaping / Humanization | 80% | 0 | Most effective single measure |
| VPN / Proxy Rotation | 50% | 3,000 | Less relevant for SMS over GSM |
| Multi-Location Deployment | 75% | 50,000 | Split across 3+ cities |
| SIM Sleeping / Rotation | 65% | 0 | Mimics normal usage patterns |
| DIRBS-Registered Devices | 40% | 10,000 | Avoids IMEI blocks only |

#### Step 6: Farm Purpose & Name

Choose from: OTP Harvesting, Bulk SMS, Social Media Farming, Call Termination, Financial Fraud, or Political Influence Operations.

#### Results

After clicking **"Deploy SIM Farm"**, the system calculates and displays:

- **Stealth Grade** (S / A / B / C / F) — color-coded card
  - **S** = Shadow — Nearly Undetectable
  - **A** = Shadow — Very Hard to Detect
  - **B** = Covert — Moderate Risk
  - **C** = Exposed — High Risk
  - **F** = Busted — Easily Detectable
- **Active SIMs** — Based on hardware slots and CNIC limits
- **SMS Throughput** — Messages per hour/day
- **Detection Risk %** — Probability of being flagged by carrier analytics
- **PTA Flag Probability %** — Chance of triggering PTA monitoring
- **Setup Cost** — One-time hardware + SIM acquisition cost in PKR
- **Monthly Operating Cost** — Ongoing SMS/data costs in PKR
- **Estimated Detection Timeline** — How long before authorities catch you
- **Warnings** — Red alerts for illegal methods, insufficient capacity, missing OPSEC
- **Educational Notes** — Facts about PTA regulations, DIRBS, NADRA biometrics, FIA investigations, and PECA 2016 penalties

---

## Instructor Playbook

### Recommended Curriculum Flow

#### Session 1: Introduction (2 hours)

1. **Lecture** (30 min): What is SIM farming? Show real-world cases — PTA crackdowns, FIA arrests, international SIM box fraud.
2. **Lab: Beginner Level** (45 min): Students individually complete all 5 Beginner exercises. Emphasize basic pattern recognition.
3. **Discussion** (15 min): What made the Beginner farm obvious? What indicators did students find?
4. **Lab: Playground** (30 min): Have students build a "Beginner-style" farm in the Playground (single carrier, no OPSEC, cheap hardware). See the F/C grade.

#### Session 2: Advanced Detection (2 hours)

1. **Lecture** (30 min): IMEI rotation, VPN tunneling, staggered activation, traffic shaping. How sophisticated farms evade basic detection.
2. **Lab: Easy Level** (60 min): Students work through all 5 Easy exercises. Encourage collaboration and discussion.
3. **Discussion** (15 min): What statistical techniques were needed? How does correlation analysis differ from pattern matching?
4. **Lab: Playground** (15 min): Students modify their farms to use OPSEC measures and see the grade improve to A/B.

#### Session 3: HUMINT & Social Engineering (2 hours)

1. **Lecture** (20 min): Why technical analysis fails against closed systems. The role of HUMINT in cybersecurity. Ethics of social engineering.
2. **Lab: Legendary Level** (30 min): Students attempt technical analysis and prove it's impossible to distinguish farm SIMs from legitimate users.
3. **Lab: Phishing Game** (45 min): Students play the phishing game. Set a minimum score threshold.
4. **Discussion** (25 min): What social engineering techniques worked? Which NPCs were most vulnerable? Ethical implications.

#### Session 4: Putting It All Together (1 hour)

1. **Lab: Playground Challenge** (30 min): Students compete to build the stealthiest farm possible (highest grade, lowest detection risk).
2. **Discussion** (30 min): How would you detect each other's farms? What regulations exist in Pakistan? Discuss PTA, DIRBS, NADRA, PECA 2016.

### Assessment Rubric

| Component | Weight | Criteria |
|---|---|---|
| Beginner Exercises | 20% | All 5 flags correct |
| Easy Exercises | 25% | All 5 flags correct |
| Legendary Analysis | 10% | Written proof that technical analysis fails |
| Phishing Game Score | 25% | Evidence collected + report quality |
| Playground Report | 20% | Built farm with analysis of detection vectors |

### Discussion Topics Per Level

**Beginner:**
- Why do amateur SIM farms still exist if they're so easy to detect?
- What telecom data is available to investigators vs. what requires a warrant?
- How do carriers automate detection of these patterns?

**Easy:**
- What is the tradeoff between OPSEC complexity and operational cost?
- How does IMEI rotation interact with Pakistan's DIRBS system?
- At what point does statistical analysis become legally admissible evidence?

**Legendary:**
- Is there an ethical framework for using social engineering in investigations?
- When does a SIM farm cross from grey area to criminal activity?
- How do intelligence agencies balance HUMINT with privacy rights?
- Under PECA 2016, what constitutes "unauthorized access" in a phishing context?

**Playground:**
- What would it take to build an "S-grade" farm? Is it economically viable?
- How does the Pakistani regulatory environment (PTA, DIRBS, biometric verification) compare to other countries?
- If you were designing detection systems for PTA, what would you monitor?

---

## Architecture

```
simfarm-lab/
├── backend/
│   ├── main.py                # FastAPI app, all REST endpoints
│   ├── simulator/
│   │   ├── models.py          # Data models (SIMCard, CDR, NetworkLog)
│   │   ├── beginner.py        # Beginner scenario generator
│   │   ├── easy.py            # Easy scenario generator
│   │   ├── legendary.py       # Legendary scenario generator
│   │   └── playground.py      # Playground farm builder + Pakistani telecom data
│   ├── detection/
│   │   ├── engine.py          # 7 analysis tools
│   │   └── exercises.py       # 12 flag-based exercises
│   └── phishing/
│       └── game.py            # Phishing game engine, 5 NPCs, evidence system
├── frontend/
│   ├── index.html             # Single-page app
│   ├── css/style.css          # Dark cybersecurity theme
│   └── js/
│       ├── api.js             # API client
│       ├── app.js             # App initialization
│       ├── dashboard.js       # Level selection dashboard
│       ├── lab.js             # Lab view (data explorer, analysis, exercises)
│       ├── phishing.js        # Phishing game UI
│       └── playground.js      # Playground wizard UI
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

**Tech stack:** Python 3.11 + FastAPI, SQLite (in-memory), Vanilla HTML/CSS/JS, Docker.

---

## API Reference

All endpoints are served from `http://localhost:8000`.

### Levels & Scenarios

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/levels` | List all 3 difficulty levels |
| `POST` | `/api/scenario/{level}` | Generate scenario data for a level |
| `GET` | `/api/scenario/{level}/sims?page=1&per_page=50` | Paginated SIM card data |
| `GET` | `/api/scenario/{level}/cdrs?page=1&per_page=100` | Paginated CDR records |
| `GET` | `/api/scenario/{level}/network-logs?page=1&per_page=100` | Paginated network logs |

### Analysis

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/analysis-tools` | List available analysis tools |
| `POST` | `/api/analyze/{level}` | Run an analysis tool on scenario data |

### Exercises

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/exercises/{level}` | Get exercises for a level |
| `POST` | `/api/exercises/submit` | Submit a flag answer |

### Phishing Game

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/phishing/new-game` | Start a new phishing game session |
| `GET` | `/api/phishing/directory` | Get NovaCom employee directory |
| `POST` | `/api/phishing/send` | Send a phishing email to an NPC |
| `GET` | `/api/phishing/status/{session_id}` | Get current game status |
| `POST` | `/api/phishing/submit-report` | Submit final investigation report |

### Playground

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/playground/options` | Get all configuration options (carriers, cities, hardware, etc.) |
| `POST` | `/api/playground/build` | Build a farm and calculate metrics |

---

## Disclaimer

This lab is provided strictly for **educational and training use** in academic and professional cybersecurity programs.

- **Do not** apply these techniques against real individuals, telecom networks, or systems without explicit authorization.
- **Do not** use the Playground configurations to plan or execute actual SIM farming operations.
- SIM farming is **illegal** in Pakistan under the Prevention of Electronic Crimes Act (PECA) 2016 and PTA regulations. Penalties include fines up to PKR 500,000 and imprisonment up to 3 years.
- The phishing techniques taught here are for **defensive training** — understanding social engineering to build better defenses.

---

## License

MIT
