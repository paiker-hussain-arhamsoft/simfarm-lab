"""TTP Reference Library — MITRE ATT&CK-style entries for SIM farm operations.

Each TTP entry follows a structured format:
- ID: SF-TXXXX (SIM Farm Technique)
- Category: maps to kill-chain phase
- Technical definition, threat assessment
- Indicators of Compromise (IoCs) for defenders
- Detection methods and countermeasures
- Ethical cover analysis (how operators disguise the technique)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TTPCategory(str, Enum):
    INFRASTRUCTURE = "infrastructure"
    ACQUISITION = "acquisition"
    IDENTITY = "identity"
    EVASION = "evasion"
    AUTOMATION = "automation"
    AMPLIFICATION = "amplification"
    PERSISTENCE = "persistence"
    EXFILTRATION = "exfiltration"


class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionDifficulty(str, Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"
    NEAR_IMPOSSIBLE = "near_impossible"


@dataclass
class IoC:
    """Indicator of Compromise."""
    indicator_type: str  # network, behavioral, temporal, physical, financial
    description: str
    detection_confidence: str  # high, medium, low
    data_source: str  # CDR, NetFlow, HLR, SIEM, financial records, etc.


@dataclass
class DetectionMethod:
    """How a defender detects this technique."""
    name: str
    description: str
    tools_required: list[str]
    effectiveness: str  # high, medium, low
    false_positive_rate: str  # high, medium, low
    skill_level_required: str  # junior, mid, senior, expert


@dataclass
class Countermeasure:
    """Defensive countermeasure against this technique."""
    name: str
    description: str
    implementation_level: str  # carrier, platform, law_enforcement, regulatory
    effectiveness: str


@dataclass
class EthicalCover:
    """How operators disguise this technique behind legitimate business."""
    claimed_purpose: str
    legitimate_equivalent: str
    red_flags: list[str]
    investigative_questions: list[str]


@dataclass
class TTPEntry:
    """A single TTP entry in the reference library."""
    id: str
    name: str
    category: TTPCategory
    threat_level: ThreatLevel
    detection_difficulty: DetectionDifficulty
    summary: str
    technical_definition: str
    how_it_works: str
    threat_description: str
    indicators: list[IoC]
    detection_methods: list[DetectionMethod]
    countermeasures: list[Countermeasure]
    ethical_cover: Optional[EthicalCover] = None
    related_ttps: list[str] = field(default_factory=list)
    real_world_examples: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    kill_chain_phase: str = ""
    beginner_visible: bool = True
    easy_visible: bool = True
    legendary_visible: bool = True


# ────────────────────────────────────────────────────────────────────
# TTP DATABASE — comprehensive entries
# ────────────────────────────────────────────────────────────────────

TTP_DATABASE: list[TTPEntry] = [

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # INFRASTRUCTURE — Setting up the farm's physical/digital backbone
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T1001",
        name="GSM Modem Bank Deployment",
        category=TTPCategory.INFRASTRUCTURE,
        threat_level=ThreatLevel.HIGH,
        detection_difficulty=DetectionDifficulty.MODERATE,
        kill_chain_phase="Resource Development",
        summary="Deployment of multi-port GSM modems (SIM boxes) to manage hundreds of SIM cards from a single location.",
        technical_definition=(
            "A GSM modem bank (commonly called a SIM box) is a hardware device containing "
            "multiple GSM radio modules, each with its own SIM slot. Enterprise-grade units "
            "support 8–256 SIM slots with hot-swap capability. The device connects to a "
            "central controller via Ethernet or USB, exposing each SIM as an AT-command "
            "endpoint. Typical chipsets: SIMCom SIM800/SIM7600, Quectel EC25/EG25."
        ),
        how_it_works=(
            "Operator inserts SIMs into a rack-mounted or desktop modem bank. Each SIM "
            "registers independently on the mobile network. Orchestration software (Gammu, "
            "Kannel, or proprietary) sends AT commands to each modem: AT+CMGS for SMS, ATD "
            "for calls. SIM rotation scripts cycle active/idle SIMs to avoid rate-limit "
            "triggers. Power and cooling are provided by the site's electrical supply."
        ),
        threat_description=(
            "Enables mass-scale messaging, OTP harvesting, and call termination fraud. "
            "A single 128-SIM box can send ~50,000 SMS/day. Combined with automation, "
            "this is the backbone of most commercial SIM farms."
        ),
        indicators=[
            IoC("rf_signal", "Unusual RF density from a single location — many simultaneous GSM registrations on the same cell sector", "high", "Cell tower logs / RF monitoring"),
            IoC("network", "Burst of IMSI attach/detach events from one cell sector within minutes", "high", "HLR/VLR logs"),
            IoC("temporal", "Regular SIM cycling patterns — SIMs activate/deactivate in rotation (e.g., 8 active, 8 idle, swap every 30 min)", "medium", "CDR analysis"),
            IoC("physical", "Elevated power consumption at a residential/commercial address inconsistent with declared use", "low", "Utility records"),
            IoC("financial", "Bulk SIM purchases from a single entity or individual exceeding normal consumer patterns", "medium", "Carrier retail records"),
        ],
        detection_methods=[
            DetectionMethod(
                "RF Anomaly Detection",
                "Deploy TSCM (Technical Surveillance Countermeasures) or use carrier-side cell congestion reports to identify locations with abnormally high simultaneous registrations.",
                ["RF spectrum analyzer", "Carrier cell congestion dashboard", "IMSI catcher (law enforcement only)"],
                "high", "low", "senior",
            ),
            DetectionMethod(
                "IMSI Attach Velocity Analysis",
                "Monitor HLR/VLR for high-frequency attach/detach events from a single cell sector. Normal: 0–5/hour. SIM box: 50–500/hour.",
                ["HLR query tools", "CDR analytics platform"],
                "high", "medium", "mid",
            ),
            DetectionMethod(
                "SIM Activation Clustering",
                "Statistical analysis of SIM activation timestamps. Farm SIMs often cluster within days/weeks. Apply K-means or DBSCAN on activation dates + cell tower.",
                ["Python/R analytics", "CDR database"],
                "medium", "medium", "mid",
            ),
        ],
        countermeasures=[
            Countermeasure("Cell Congestion Alerts", "Carrier-level alerts when a cell sector exceeds expected simultaneous registrations by >2 standard deviations.", "carrier", "high"),
            Countermeasure("SIM Registration Velocity Limits", "Rate-limit new SIM registrations per cell sector per hour.", "carrier", "medium"),
            Countermeasure("IMEI-TAC Diversity Scoring", "Flag sectors where >80% of IMEIs share the same TAC (Type Allocation Code), indicating identical modem hardware.", "carrier", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Bulk messaging service for marketing, appointment reminders, or customer notifications.",
            legitimate_equivalent="Legitimate A2P (Application-to-Person) messaging providers use carrier-approved APIs (e.g., Twilio, Vonage) rather than SIM boxes.",
            red_flags=[
                "Uses physical SIM hardware instead of API-based messaging",
                "No A2P license or carrier agreement on file",
                "Message content is not branded or includes deceptive sender IDs",
                "Operates from a residential address rather than a registered business premises",
                "Volume exceeds what a legitimate business of its declared size would send",
            ],
            investigative_questions=[
                "Does the entity hold an A2P messaging license from the carrier or regulator?",
                "Can they provide a customer list and consent records for message recipients?",
                "Is the declared business address consistent with the scale of operations?",
                "Are message templates registered and approved by the carrier?",
            ],
        ),
        related_ttps=["SF-T1002", "SF-T2001", "SF-T3001"],
        real_world_examples=[
            "2023: Nigerian SIM box fraud ring dismantled — 14,000 SIMs in Lagos apartment",
            "2022: UK Ofcom investigation into SIM boxes used for international call bypass",
        ],
    ),

    TTPEntry(
        id="SF-T1002",
        name="Distributed Phone Farm",
        category=TTPCategory.INFRASTRUCTURE,
        threat_level=ThreatLevel.HIGH,
        detection_difficulty=DetectionDifficulty.HARD,
        kill_chain_phase="Resource Development",
        summary="Racks of physical smartphones or Android emulators each running individual SIMs and social media accounts.",
        technical_definition=(
            "A phone farm is a collection of physical Android devices (or virtual Android "
            "instances) arranged in racks or shelving units. Each device holds a SIM card and "
            "runs social media apps with unique accounts. Devices are managed via ADB (Android "
            "Debug Bridge) over USB hubs or WiFi. Automation is achieved through accessibility "
            "services, Appium, or modified APKs."
        ),
        how_it_works=(
            "Devices are connected to multi-port USB hubs (30–60 ports) linked to a control "
            "PC. ADB scripts push commands to each device: tap coordinates, type text, swipe. "
            "Each device has a unique Google account, SIM, IMEI, and MAC address. Devices are "
            "assigned to accounts 1:1. Over-the-air (OTA) updates are disabled. Apps are frozen "
            "at specific versions to prevent anti-farm detection updates."
        ),
        threat_description=(
            "Phone farms generate authentic-looking social media engagement because each account "
            "runs on a real device with real cellular connectivity. Platform anti-fraud systems "
            "that fingerprint devices see each as a legitimate user. Used for astroturfing, "
            "app install fraud, fake reviews, and political influence operations."
        ),
        indicators=[
            IoC("behavioral", "Many accounts from same geographic cluster posting similar content within a short time window", "medium", "Platform content analysis"),
            IoC("network", "Multiple devices on the same WiFi access point or IP subnet, but each with unique cellular data (split tunneling)", "medium", "Network traffic logs"),
            IoC("temporal", "Identical interaction timing patterns across accounts — e.g., all like a post within a 2-minute window", "high", "Platform engagement logs"),
            IoC("physical", "Unusual power draw or data usage from a premises inconsistent with its declared use", "low", "ISP / utility records"),
            IoC("behavioral", "Device telemetry shows OTA updates disabled and developer mode enabled across many devices on same subnet", "medium", "Google Play Protect / MDM telemetry"),
        ],
        detection_methods=[
            DetectionMethod(
                "Coordinated Inauthentic Behavior (CIB) Analysis",
                "Graph analysis of engagement patterns — cluster accounts that consistently engage with the same content within tight time windows. Inferred from platform data, not carrier data.",
                ["Graph database (Neo4j)", "Social network analysis tools", "Platform API access"],
                "high", "medium", "senior",
            ),
            DetectionMethod(
                "Device Fingerprint Correlation",
                "Even with unique IMEIs, devices may share: WiFi BSSID in background scans, GPS clusters, accelerometer noise profiles (from identical hardware). Requires platform-side telemetry.",
                ["Platform device telemetry", "Machine learning classifier"],
                "medium", "low", "expert",
            ),
        ],
        countermeasures=[
            Countermeasure("CIB Graph Analysis", "Platform-side graph clustering to detect coordinated engagement rings.", "platform", "high"),
            Countermeasure("Hardware Attestation", "Require SafetyNet/Play Integrity attestation for account creation to block emulators and tampered devices.", "platform", "medium"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="App testing farm, quality assurance lab, or mobile marketing agency doing real-device testing.",
            legitimate_equivalent="Legitimate device farms (BrowserStack, AWS Device Farm, Samsung Remote Test Lab) are cloud-hosted with audit trails and don't require SIM cards in each device.",
            red_flags=[
                "Each device has a unique SIM card (real QA farms use WiFi-only or eSIM test profiles)",
                "Social media apps are the primary workload rather than the app being 'tested'",
                "No QA test scripts, bug reports, or JIRA tickets associated with the 'testing' activity",
                "The 'tested' app is always the same social media platform, not a client's product",
                "Devices are running consumer accounts, not test/sandbox accounts",
            ],
            investigative_questions=[
                "Can the entity produce QA test plans and bug reports from the device farm?",
                "Are the social media accounts linked to real, verifiable identities?",
                "Why does each device need a unique SIM if it's a testing operation?",
                "Is the entity a registered software testing or marketing company?",
            ],
        ),
        related_ttps=["SF-T1001", "SF-T3002", "SF-T5001"],
    ),

    TTPEntry(
        id="SF-T1003",
        name="Residential Proxy Infrastructure",
        category=TTPCategory.INFRASTRUCTURE,
        threat_level=ThreatLevel.CRITICAL,
        detection_difficulty=DetectionDifficulty.VERY_HARD,
        kill_chain_phase="Resource Development",
        summary="Routing farm traffic through residential IP addresses to avoid datacenter/VPN detection.",
        technical_definition=(
            "Residential proxies are IP addresses assigned by ISPs to home users. Proxy "
            "providers (Bright Data, Oxylabs, SOAX, SmartProxy, etc.) aggregate residential "
            "IPs by installing SDK-based proxy agents in mobile apps and browser extensions "
            "(users opt-in, often unknowingly, via free VPN/utility apps). The SIM farm routes "
            "each account's traffic through a different residential IP, making it appear that "
            "each account operates from a different household."
        ),
        how_it_works=(
            "The farm operator subscribes to a residential proxy provider and receives API "
            "access or SOCKS5/HTTP proxy endpoints with geo-targeting. Each social media "
            "account is configured with a sticky session to a specific residential IP in the "
            "target geography. IP rotation policies ensure no two accounts share an IP. "
            "Advanced setups use backconnect proxies that auto-rotate while maintaining "
            "session cookies."
        ),
        threat_description=(
            "Residential proxies defeat the most common anti-fraud measure: IP reputation "
            "scoring. Since the IPs belong to real ISP customers, they pass all blocklists "
            "and geo-checks. This makes the farm's accounts indistinguishable from real users "
            "at the network layer. Combined with device fingerprint spoofing, this is the "
            "single most effective evasion technique."
        ),
        indicators=[
            IoC("network", "Traffic to known residential proxy provider API endpoints (e.g., zproxy.lum-superproxy.io, proxy.soax.com)", "high", "DNS / NetFlow logs"),
            IoC("network", "HTTP headers containing X-Forwarded-For chains or proxy-specific headers", "medium", "Deep packet inspection"),
            IoC("behavioral", "An account's apparent IP geolocates to a different region than its SIM card's HLR registration", "medium", "Cross-referencing CDR + platform IP logs"),
            IoC("financial", "Subscription payments to residential proxy providers (Bright Data, Oxylabs, SmartProxy, SOAX)", "high", "Financial records / payment processor data"),
        ],
        detection_methods=[
            DetectionMethod(
                "Proxy Provider Endpoint Blocklisting",
                "Maintain and update blocklists of known residential proxy provider API domains and IP ranges. Monitor DNS queries from suspect devices.",
                ["DNS monitoring", "Threat intelligence feeds (IPQualityScore, MaxMind)"],
                "medium", "medium", "mid",
            ),
            DetectionMethod(
                "IP-HLR Geolocation Mismatch",
                "Cross-reference the SIM's HLR-registered location with the IP geolocation of the account's web/API traffic. Legitimate users: these match. Farm accounts using proxies: they often diverge.",
                ["HLR lookup tools", "IP geolocation database", "Platform login IP logs"],
                "high", "low", "senior",
            ),
        ],
        countermeasures=[
            Countermeasure("IP Intelligence Scoring", "Use services like MaxMind, IPQualityScore, or Spur.us to score IP addresses for proxy/VPN probability at login.", "platform", "medium"),
            Countermeasure("SIM-IP Location Correlation", "At carrier level, compare the cell tower location of a SIM with the IP geolocation of its data session. Persistent mismatches indicate proxying.", "carrier", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Web scraping for price comparison, ad verification, SEO research, or academic research requiring geo-diverse data collection.",
            legitimate_equivalent="Legitimate web scraping uses datacenter proxies or APIs with published ToS compliance. Academic research discloses proxy use in methodology.",
            red_flags=[
                "Residential proxy usage combined with social media account management (not just data collection)",
                "Proxy sessions are sticky per-account (maintaining identity) rather than rotating (collecting data)",
                "Volume of proxy usage is disproportionate to the declared scraping/research scope",
                "No published research papers, price comparison datasets, or ad verification reports produced",
            ],
            investigative_questions=[
                "What data is being collected via the residential proxies? Can they show outputs?",
                "Why do they need geo-targeted sticky sessions rather than rotating datacenter proxies?",
                "Is the proxy traffic going to social media platforms or to the declared data sources?",
            ],
        ),
        related_ttps=["SF-T4001", "SF-T4004"],
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ACQUISITION — Obtaining SIM cards at scale
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T2001",
        name="Bulk PAYG SIM Procurement",
        category=TTPCategory.ACQUISITION,
        threat_level=ThreatLevel.MEDIUM,
        detection_difficulty=DetectionDifficulty.EASY,
        kill_chain_phase="Resource Development",
        summary="Purchasing large quantities of prepaid SIM cards from retail channels without identity verification.",
        technical_definition=(
            "In jurisdictions without mandatory SIM registration (UK, USA pre-2024, parts of "
            "EU), prepaid (PAYG) SIM cards are available over the counter at convenience stores, "
            "supermarkets, and online marketplaces with no ID check. Operators purchase hundreds "
            "to thousands of SIMs across multiple retail locations to avoid triggering bulk-sale "
            "alerts."
        ),
        how_it_works=(
            "Operators use multiple individuals ('runners') to purchase SIMs from different "
            "stores in different cities. SIMs are activated using burner email addresses. "
            "In countries with SIM registration (Pakistan, India, Nigeria), runners use stolen "
            "or borrowed identity documents. In the UK, SIMs from giffgaff, Lycamobile, Lebara, "
            "and Three can be ordered online in bulk with no questions asked."
        ),
        threat_description=(
            "Provides the farm with anonymous, untraceable phone numbers. Without SIM registration, "
            "these numbers cannot be linked to a real identity, making law enforcement tracing "
            "extremely difficult. The low cost (often free or <$1 per SIM) makes scaling cheap."
        ),
        indicators=[
            IoC("financial", "Multiple SIM purchases from the same payment method or shipping address within days", "high", "Carrier retail/fulfillment records"),
            IoC("behavioral", "Dozens of SIM activations from the same IMEI (device) — indicates SIMs being tested in the same modem", "high", "HLR logs"),
            IoC("temporal", "Cluster of SIM activations within hours/days that later show coordinated activity", "medium", "CDR analytics"),
            IoC("physical", "Same shipping address receiving SIMs from multiple carriers", "medium", "Carrier fulfillment data"),
        ],
        detection_methods=[
            DetectionMethod(
                "IMEI-to-SIM Ratio Analysis",
                "Track how many unique SIMs have been activated on each IMEI. Legitimate: 1–3 SIMs per IMEI over years. Farm: 10–100+ SIMs per IMEI.",
                ["HLR/EIR database", "CDR analytics"],
                "high", "low", "junior",
            ),
            DetectionMethod(
                "Activation Burst Detection",
                "Monitor for spikes in SIM activations from a single cell tower or postcode. Apply statistical process control (SPC) charts.",
                ["CDR database", "Statistical analysis tools"],
                "medium", "medium", "mid",
            ),
        ],
        countermeasures=[
            Countermeasure("Mandatory SIM Registration", "Require government-issued ID for every SIM purchase (as in Pakistan DIRBS, India Aadhaar, Turkey).", "regulatory", "high"),
            Countermeasure("Bulk Purchase Limits", "Carriers cap SIM sales per individual/address (e.g., max 5 per 30 days).", "carrier", "medium"),
            Countermeasure("Cross-Carrier SIM Purchase Database", "Shared database between carriers to detect individuals buying across carriers.", "regulatory", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Purchasing SIMs for IoT devices, fleet management, vending machines, or employee distribution.",
            legitimate_equivalent="Legitimate IoT/M2M deployments use dedicated M2M SIM plans from carriers with registered business accounts and static IPs.",
            red_flags=[
                "SIMs are consumer PAYG, not M2M/IoT plans",
                "No IoT device fleet or business justification documented",
                "SIMs are used for voice/SMS rather than low-bandwidth IoT data",
                "Purchased from consumer retail channels rather than carrier business sales",
            ],
            investigative_questions=[
                "Can the entity document the IoT devices these SIMs are installed in?",
                "Why use consumer PAYG plans instead of carrier M2M plans?",
                "Is the traffic profile consistent with IoT (small data packets) or social media (high data + SMS)?",
            ],
        ),
        related_ttps=["SF-T1001", "SF-T2002"],
    ),

    TTPEntry(
        id="SF-T2002",
        name="Identity Document Exploitation",
        category=TTPCategory.ACQUISITION,
        threat_level=ThreatLevel.CRITICAL,
        detection_difficulty=DetectionDifficulty.HARD,
        kill_chain_phase="Resource Development",
        summary="Using stolen, borrowed, or synthetic identity documents to register SIM cards in jurisdictions requiring ID verification.",
        technical_definition=(
            "In countries with mandatory SIM registration (Pakistan NADRA/DIRBS, India Aadhaar, "
            "Nigeria NIN-SIM, Turkey e-Devlet), each SIM must be linked to a government-issued ID. "
            "Farm operators circumvent this by using stolen ID numbers, paying individuals to register "
            "SIMs in their name ('SIM mules'), exploiting corrupt carrier agents who bypass biometric "
            "checks, or using deepfake-generated biometric data."
        ),
        how_it_works=(
            "Method 1 — SIM mules: Low-income individuals are paid a small fee to register SIMs "
            "in their name. They may not know the SIMs will be used for fraud. "
            "Method 2 — Corrupt agents: Carrier retail agents are bribed to skip biometric/ID verification "
            "or to use a template ID for multiple registrations. "
            "Method 3 — Stolen credentials: Leaked databases provide name + ID number pairs. In systems "
            "without live biometric checks, this is sufficient. "
            "Method 4 — Synthetic identity: Generate realistic but fictitious ID credentials using AI "
            "tools, paired with deepfake biometrics for liveness checks."
        ),
        threat_description=(
            "Breaks the fundamental assumption of SIM registration — that each SIM traces to a real "
            "person. Enables farms to operate at scale even in high-regulation environments. "
            "The mule network model also victimises the individuals whose identities are used."
        ),
        indicators=[
            IoC("behavioral", "A single ID number linked to many SIMs across carriers (exceeds per-person SIM limits)", "high", "Cross-carrier SIM registration database"),
            IoC("behavioral", "SIMs registered to elderly, deceased, or incarcerated individuals showing active social media usage", "high", "Civil registry cross-reference"),
            IoC("financial", "Carrier agent with abnormally high registration volume compared to peers at the same store", "medium", "Carrier HR/audit data"),
            IoC("temporal", "Many SIM registrations from the same agent within minutes, but no corresponding foot traffic at the store", "medium", "Store CCTV + registration logs"),
        ],
        detection_methods=[
            DetectionMethod(
                "SIM-per-ID Ratio Monitoring",
                "Cross-carrier database query: flag any ID linked to more SIMs than the legal limit (e.g., Pakistan: 5 SIMs per CNIC).",
                ["National SIM registration database (e.g., DIRBS)", "Cross-carrier data sharing agreement"],
                "high", "low", "junior",
            ),
            DetectionMethod(
                "Biometric Liveness Anomaly Detection",
                "Monitor for repeated liveness check failures followed by a success (indicating spoofing attempts), or identical biometric templates across registrations.",
                ["Biometric verification logs", "AI liveness detection system"],
                "medium", "medium", "senior",
            ),
        ],
        countermeasures=[
            Countermeasure("Live Biometric Verification", "Require real-time fingerprint/face scan at point of sale with liveness detection (anti-deepfake).", "carrier", "high"),
            Countermeasure("Cross-Carrier Registration Limits", "National database enforcing max SIMs per ID across all carriers (e.g., Pakistan DIRBS).", "regulatory", "high"),
            Countermeasure("Agent Audit Programs", "Random audits of carrier retail agents' registration accuracy, with penalties for discrepancies.", "carrier", "medium"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Registering SIMs for family members, employees, or community members who cannot visit the store themselves.",
            legitimate_equivalent="Legitimate proxy registration (where allowed) requires a notarised power of attorney and the registered person's direct consent.",
            red_flags=[
                "The same person registers SIMs for dozens of 'family members' who never contact the carrier",
                "Registered 'employees' don't appear in any business payroll or tax records",
                "Biometric data shows low-confidence matches or repeated attempts",
                "SIMs registered to one person but physically located in a different city",
            ],
            investigative_questions=[
                "Can each registered individual confirm they authorised the SIM registration?",
                "Do the registered individuals physically possess the SIM cards?",
                "Does the traffic pattern match the registered individual's profile (age, location, lifestyle)?",
            ],
        ),
        related_ttps=["SF-T2001", "SF-T3001"],
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # IDENTITY — Creating and managing fake personas
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T3001",
        name="Persona Generation and Aging",
        category=TTPCategory.IDENTITY,
        threat_level=ThreatLevel.HIGH,
        detection_difficulty=DetectionDifficulty.VERY_HARD,
        kill_chain_phase="Resource Development",
        summary="Creating fake social media identities with realistic profiles and 'aging' them over weeks/months to build credibility.",
        technical_definition=(
            "Persona generation is the creation of a complete digital identity: name, profile "
            "photo (AI-generated via StyleGAN/Stable Diffusion or stock photo), bio, employment "
            "history, interests, and social connections. Aging (also called 'warming' or 'curing') "
            "is the process of making the account look established by posting non-controversial "
            "content, following real accounts, and gradually building a follower base over weeks "
            "to months before deploying the account for its real purpose."
        ),
        how_it_works=(
            "Phase 1 — Generation: Automated scripts create accounts on target platforms using "
            "unique email, phone number (from SIM), name (from name generators weighted by "
            "target demographics), and AI-generated profile photo. Bio is templated from real "
            "profiles in the target demographic. "
            "Phase 2 — Aging: For 2–12 weeks, the account posts lifestyle content (food photos, "
            "pet pictures, weather comments, local news reactions), follows local accounts, joins "
            "interest groups, and reacts to content. This builds 'account trust scores' on the "
            "platform's anti-spam systems. "
            "Phase 3 — Deployment: Once the account passes trust thresholds, it's deployed for "
            "its real purpose: political messaging, product promotion, or influence operations."
        ),
        threat_description=(
            "Aged accounts are significantly harder to detect than fresh accounts. Platform "
            "anti-spam systems score accounts based on age, activity history, and social graph "
            "density. A 3-month-old account with 200 posts and 150 followers is treated as "
            "legitimate by most detection systems. This is the most resource-intensive but "
            "most effective technique in the SIM farm operator's arsenal."
        ),
        indicators=[
            IoC("behavioral", "Profile photos fail reverse image search but show GAN artifacts (symmetric face, blurred ears, inconsistent background)", "medium", "Image forensics tools"),
            IoC("behavioral", "Account's 'aging' content is generic and impersonal — no photos of friends, no location check-ins, no personal anecdotes", "medium", "Content analysis"),
            IoC("temporal", "Sudden shift from lifestyle content to political/promotional content after weeks of inactivity or bland posting", "high", "Platform content timeline analysis"),
            IoC("behavioral", "Account follows a disproportionate number of news/political accounts compared to personal connections", "medium", "Social graph analysis"),
            IoC("network", "Multiple accounts share the same posting schedule pattern (same active hours, same post frequency distribution)", "high", "Cross-account temporal analysis"),
        ],
        detection_methods=[
            DetectionMethod(
                "GAN-Generated Image Detection",
                "Use classifiers trained on StyleGAN/DALL-E/Midjourney outputs to detect AI-generated profile photos. Tools: FotoForensics, Microsoft Video Authenticator, custom CNN classifiers.",
                ["AI image detection models", "Reverse image search API"],
                "medium", "medium", "mid",
            ),
            DetectionMethod(
                "Content Phase Transition Analysis",
                "Detect accounts whose content topic and tone shifts abruptly — from generic lifestyle to political messaging. NLP-based topic modelling over time (LDA, BERTopic).",
                ["NLP pipeline", "Topic modelling tools", "Platform content API"],
                "high", "low", "senior",
            ),
            DetectionMethod(
                "Social Graph Sparsity Scoring",
                "Measure the density and reciprocity of an account's social connections. Farm accounts typically have low reciprocity (they follow many but few follow back) and cluster with other farm accounts.",
                ["Graph database", "Social network analysis (SNA) tools"],
                "high", "medium", "senior",
            ),
        ],
        countermeasures=[
            Countermeasure("AI Profile Photo Detection", "Automated scanning of new profile photos for GAN artifacts during account creation.", "platform", "medium"),
            Countermeasure("Behavioral Biometrics", "Track typing patterns, scroll behavior, and interaction timing to distinguish human from bot accounts.", "platform", "high"),
            Countermeasure("Account Trust Scoring", "Multi-factor trust score combining account age, content diversity, social reciprocity, and device attestation.", "platform", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Managing social media accounts for a marketing agency, managing brand ambassador accounts, or running community manager accounts.",
            legitimate_equivalent="Legitimate social media management uses branded accounts linked to real employees with disclosed agency relationships.",
            red_flags=[
                "Accounts claim to be private individuals, not branded/business accounts",
                "No disclosure of management relationship (violates FTC/ASA guidelines)",
                "Profile photos are AI-generated rather than real employee photos",
                "Accounts have no offline footprint (no LinkedIn, no company website listing)",
                "Many accounts share similar writing style or post at identical times",
            ],
            investigative_questions=[
                "Can the agency identify the real person behind each managed account?",
                "Are the accounts disclosed as managed/sponsored content per advertising standards?",
                "Do the accounts engage in activities beyond the declared management scope?",
            ],
        ),
        related_ttps=["SF-T3002", "SF-T5001", "SF-T6001"],
    ),

    TTPEntry(
        id="SF-T3002",
        name="Anti-Detect Browser Fingerprinting",
        category=TTPCategory.IDENTITY,
        threat_level=ThreatLevel.HIGH,
        detection_difficulty=DetectionDifficulty.VERY_HARD,
        kill_chain_phase="Defense Evasion",
        summary="Using specialised browsers that generate unique device fingerprints per account to defeat browser-based tracking.",
        technical_definition=(
            "Anti-detect browsers (Multilogin, GoLogin, AdsPower, Dolphin Anty, Kameleo) create "
            "isolated browser profiles, each with a unique canvas fingerprint, WebGL hash, audio "
            "context, navigator.plugins list, screen resolution, timezone, language, and WebRTC "
            "local IP. This makes each browser profile appear to be a completely different device "
            "to platform fingerprinting systems."
        ),
        how_it_works=(
            "The operator creates a browser profile for each social media account. The anti-detect "
            "browser spoofs ~40 fingerprinting vectors including: canvas rendering (by adding "
            "imperceptible noise to canvas output), WebGL vendor/renderer strings, AudioContext "
            "sample rates, screen dimensions, installed fonts, battery status, and hardware "
            "concurrency. Each profile connects through its own proxy (residential, mobile, or "
            "datacenter). Profile data is stored locally or in the cloud for team sharing."
        ),
        threat_description=(
            "Defeats the primary web-based identity verification mechanism. Platforms like "
            "Facebook, Twitter/X, and Google use browser fingerprinting as a secondary "
            "authentication signal. When each account has a unique fingerprint, platform systems "
            "cannot link accounts to the same operator, even if they're all running on one machine."
        ),
        indicators=[
            IoC("network", "DNS or HTTP traffic to anti-detect browser license servers (e.g., api.multilogin.com, app.gologin.com, api.adspower.net)", "high", "DNS/NetFlow logs"),
            IoC("behavioral", "Browser fingerprint entropy is unusually consistent — real users have messy, evolving fingerprints; spoofed ones are perfectly stable", "medium", "Platform-side fingerprint analysis"),
            IoC("behavioral", "Canvas fingerprint shows noise patterns characteristic of a specific anti-detect tool (signature analysis)", "medium", "Canvas forensics"),
            IoC("financial", "Subscription payments to anti-detect browser providers", "high", "Financial records"),
        ],
        detection_methods=[
            DetectionMethod(
                "Fingerprint Entropy Analysis",
                "Real browser fingerprints change subtly over time (browser updates, driver updates). Spoofed fingerprints are either too stable (never change) or change in unnatural ways (complete regeneration). Track fingerprint evolution per account.",
                ["Platform fingerprint database", "Statistical analysis"],
                "medium", "medium", "expert",
            ),
            DetectionMethod(
                "Canvas Noise Signature Detection",
                "Anti-detect browsers add noise to canvas output using specific algorithms. These algorithms leave detectable patterns. Extract canvas render difference between expected output (based on declared GPU) and actual output.",
                ["Canvas fingerprint database", "Image analysis tools"],
                "medium", "low", "expert",
            ),
        ],
        countermeasures=[
            Countermeasure("Behavioral Biometrics", "Track mouse movement patterns, keystroke dynamics, scroll behavior — these are much harder to spoof than browser fingerprints.", "platform", "high"),
            Countermeasure("Hardware Attestation (WebAuthn)", "Require hardware security key or platform authenticator for account actions, binding the account to physical hardware.", "platform", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Managing multiple e-commerce stores (each needs a separate browser profile), affiliate marketing, or privacy protection.",
            legitimate_equivalent="Legitimate multi-account management uses platform-approved business manager tools (Meta Business Suite, Google Ads Manager) rather than fingerprint spoofing.",
            red_flags=[
                "Social media accounts are the primary use, not e-commerce",
                "No corresponding e-commerce listings or affiliate partnerships",
                "Number of profiles far exceeds any reasonable multi-store operation",
                "Profiles are used for engagement (likes, comments, shares) rather than storefront management",
            ],
            investigative_questions=[
                "Can the operator show the e-commerce stores corresponding to each browser profile?",
                "What is the business justification for needing unique fingerprints per profile?",
                "Are the profiles used for content consumption/engagement or store management?",
            ],
        ),
        related_ttps=["SF-T1003", "SF-T3001", "SF-T4001"],
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EVASION — Avoiding detection by carriers and platforms
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T4001",
        name="IMEI/IMSI Rotation",
        category=TTPCategory.EVASION,
        threat_level=ThreatLevel.HIGH,
        detection_difficulty=DetectionDifficulty.HARD,
        kill_chain_phase="Defense Evasion",
        summary="Programmatically changing IMEI and IMSI values to prevent device tracking and SIM-device correlation.",
        technical_definition=(
            "IMEI (International Mobile Equipment Identity) identifies the physical device; "
            "IMSI (International Mobile Subscriber Identity) identifies the SIM card on the "
            "network. Advanced SIM boxes and modified firmware allow operators to change these "
            "values programmatically. IMEI changing is done via AT+EGMR commands on Qualcomm/"
            "MediaTek chipsets or via custom firmware. IMSI rotation requires SIM card-level "
            "modifications (writable SIMs or eSIM profiles)."
        ),
        how_it_works=(
            "GSM modem firmware is modified to accept AT+EGMR writes, allowing the IMEI to "
            "be changed per-SIM or on a schedule. Some SIM boxes (e.g., Dinstar, Ejoin, Hybertone) "
            "have built-in IMEI rotation — each SIM slot can be assigned a random IMEI from a "
            "pool of valid TACs. This breaks the carrier's ability to correlate 'this SIM was "
            "in this device' because the device identifier keeps changing. Advanced operators "
            "use IMEI values harvested from real devices (via public IMEI databases or device "
            "repair shops) to ensure the IMEI passes TAC validation."
        ),
        threat_description=(
            "Defeats device-based detection. Carriers track anomalies like 'one device with 100 "
            "SIMs' or 'all SIMs in identical devices.' IMEI rotation makes each SIM appear to be "
            "in a different, unique device. Combined with SIM cycling, this eliminates the primary "
            "carrier-side detection vector."
        ),
        indicators=[
            IoC("network", "IMEI changes for the same IMSI (SIM) across consecutive network registrations — legitimate users almost never change devices multiple times per day", "high", "EIR (Equipment Identity Register) logs"),
            IoC("network", "IMEIs from the same TAC prefix cluster on a single cell sector — indicates identical modem hardware despite 'different' IMEIs", "medium", "CDR + EIR analysis"),
            IoC("network", "IMEI fails TAC validation entirely (generated, not from a real device) or maps to a device model inconsistent with the network's radio capabilities", "high", "GSMA TAC database cross-reference"),
            IoC("temporal", "Periodic IMEI changes on a fixed schedule (e.g., every 24 or 48 hours) — human device changes are event-driven, not scheduled", "high", "CDR time-series analysis"),
        ],
        detection_methods=[
            DetectionMethod(
                "IMEI Change Velocity Tracking",
                "Monitor the EIR for IMSI-IMEI pair changes. Flag any IMSI that changes IMEI more than once per month. Correlate with cell tower to check if the SIM is moving (legitimate phone swap) or stationary (modem IMEI rotation).",
                ["EIR database", "CDR analytics platform"],
                "high", "low", "mid",
            ),
            DetectionMethod(
                "TAC Validation and Consistency Check",
                "Cross-reference every IMEI's TAC against the GSMA TAC database. Flag invalid TACs. For valid TACs, check if the declared device model's radio capabilities match the network features the SIM is using (e.g., an 'iPhone 15' IMEI on a 2G-only connection).",
                ["GSMA TAC database", "EIR logs"],
                "high", "low", "junior",
            ),
        ],
        countermeasures=[
            Countermeasure("IMEI Change Rate Limiting", "Carrier EIR policy: block or flag any SIM that changes IMEI more than 2x per 30-day period.", "carrier", "high"),
            Countermeasure("IMEI-TAC Blocklisting", "Maintain a blocklist of TACs associated with SIM box hardware manufacturers (Dinstar, Ejoin, Hybertone, Goip).", "carrier", "high"),
            Countermeasure("IMEI Consistency Scoring", "Score each IMEI on consistency: does the device model match the radio access technology, is the TAC valid, does the user behavior match the device segment.", "carrier", "medium"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Privacy protection, avoiding device tracking by advertisers, or testing mobile applications across different device profiles.",
            legitimate_equivalent="Legitimate device testing uses real devices or cloud device farms (AWS, BrowserStack) with valid IMEIs. Privacy-conscious users use VPNs, not IMEI spoofing.",
            red_flags=[
                "IMEI changing is illegal in many jurisdictions (UK: Section 1 Mobile Telephones (Re-programming) Act 2002)",
                "The entity cannot produce a legitimate testing use case for IMEI modification",
                "IMEIs being used are harvested from other devices (identity theft)",
                "Rotation happens on a fixed schedule rather than as part of documented test procedures",
            ],
            investigative_questions=[
                "Is there a documented software testing plan requiring IMEI modification?",
                "Are the modified IMEIs from the entity's own inventory of physical devices?",
                "In what jurisdiction are they operating, and is IMEI modification legal there?",
            ],
        ),
        related_ttps=["SF-T1001", "SF-T4002", "SF-T4003"],
    ),

    TTPEntry(
        id="SF-T4002",
        name="Traffic Shaping and Human Mimicry",
        category=TTPCategory.EVASION,
        threat_level=ThreatLevel.CRITICAL,
        detection_difficulty=DetectionDifficulty.NEAR_IMPOSSIBLE,
        kill_chain_phase="Defense Evasion",
        summary="Shaping message timing, volume, and content patterns to statistically mimic legitimate human users.",
        technical_definition=(
            "Traffic shaping in the SIM farm context means engineering the timing, volume, "
            "and type distribution of each SIM's communications to match statistical models of "
            "real human behavior. This involves Poisson process-based inter-message intervals, "
            "circadian rhythm simulation (reduced activity at night), weekday/weekend variation, "
            "and realistic SMS-to-voice-to-data ratios per persona archetype."
        ),
        how_it_works=(
            "Each SIM is assigned a persona archetype (student, professional, retiree, etc.) "
            "with associated parameters: active hours, message rate, call frequency, data usage. "
            "The orchestration software generates events using a Poisson process with the persona's "
            "rate parameter, adding jitter from a normal distribution. Sleep periods generate only "
            "occasional background data syncs. Weekday/weekend behavior differs. The result is "
            "that each SIM's CDR, when analysed statistically, is indistinguishable from a real "
            "user of that demographic."
        ),
        threat_description=(
            "Defeats statistical detection methods entirely. Temporal pattern analysis, traffic "
            "volume anomaly detection, and behavioral profiling all rely on farm SIMs deviating "
            "from normal human patterns. When the farm explicitly models human patterns, these "
            "methods produce no signal. This is the single most impactful evasion technique for "
            "a 'legendary' farm and represents the highest tier of operational sophistication."
        ),
        indicators=[
            IoC("behavioral", "Persona parameters are TOO consistent over time — real humans have life events, mood changes, travel that cause irregular deviations; perfectly smooth statistical distributions are suspicious", "low", "Long-term CDR analysis (6+ months)"),
            IoC("behavioral", "Zero emergency or 999/911/112 calls across entire fleet — every real population segment occasionally makes emergency calls", "low", "CDR aggregate analysis"),
            IoC("behavioral", "No international roaming events across entire fleet — statistically improbable for a real user population over 12+ months", "low", "CDR aggregate analysis"),
            IoC("behavioral", "Persona archetypes appear to be drawn from a fixed set — e.g., exactly 7 distinct behavioral profiles, each replicated many times", "medium", "Behavioral clustering (unsupervised ML)"),
        ],
        detection_methods=[
            DetectionMethod(
                "Distribution Conformity Testing (Over-Fitting Detection)",
                "Real human behavior is messy — it doesn't perfectly conform to statistical models. Apply goodness-of-fit tests (KS test, Anderson-Darling) to individual SIM CDR distributions. If a SIM's timing fits a Poisson process TOO well (p > 0.95), it may be synthetic.",
                ["Statistical analysis platform (R/Python)", "CDR database", "High-volume computing"],
                "medium", "high", "expert",
            ),
            DetectionMethod(
                "Fleet-Level Anomaly Detection",
                "Even if individual SIMs pass tests, the FLEET as a whole may show anomalies: no emergency calls, no roaming, uniform persona distribution, no SIM churn. Compare fleet-level statistics to expected population baselines.",
                ["CDR aggregate analytics", "Population baseline data"],
                "medium", "medium", "expert",
            ),
        ],
        countermeasures=[
            Countermeasure("Multi-Signal Correlation", "Combine CDR analysis with social graph analysis, platform engagement patterns, and device telemetry for a holistic score.", "carrier", "medium"),
            Countermeasure("Longitudinal Behavior Tracking", "Track behavioral consistency over 12+ months. Real users show life events (travel, job change, relationship changes) that alter patterns.", "carrier", "medium"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Load testing or stress testing telecom infrastructure by simulating realistic user traffic patterns.",
            legitimate_equivalent="Carrier-approved load testing uses synthetic traffic on isolated test networks, not real commercial spectrum. It is coordinated with the carrier's engineering team.",
            red_flags=[
                "Traffic is on the live commercial network, not a test/lab environment",
                "No carrier engineering team is aware of the 'load test'",
                "The 'test traffic' includes real message content to real recipients, not test numbers",
                "Duration extends beyond any reasonable testing window (weeks/months vs. hours)",
            ],
            investigative_questions=[
                "Is there a signed agreement with the carrier to conduct load testing on their network?",
                "Are the test results being documented and shared with the carrier's engineering team?",
                "Why does the 'test' require real SIM cards and real phone numbers rather than a lab environment?",
            ],
        ),
        related_ttps=["SF-T4001", "SF-T4003", "SF-T5001"],
    ),

    TTPEntry(
        id="SF-T4003",
        name="Geographic Distribution and Tower Hopping",
        category=TTPCategory.EVASION,
        threat_level=ThreatLevel.HIGH,
        detection_difficulty=DetectionDifficulty.HARD,
        kill_chain_phase="Defense Evasion",
        summary="Physically distributing SIMs across many cell towers or simulating movement between towers.",
        technical_definition=(
            "Tower hopping distributes SIM farm hardware across multiple physical locations so "
            "SIMs register on different cell towers. Alternatively, some SIM boxes have directional "
            "antenna arrays that can register on specific towers. This prevents the 'many SIMs on "
            "one tower' detection signal."
        ),
        how_it_works=(
            "Method 1 — Physical distribution: SIM boxes or phones are placed in multiple safe "
            "houses, coworking spaces, or rented premises across a city. Each location has 20–50 "
            "SIMs, mimicking a normal household/office density. Central control via VPN. "
            "Method 2 — Mobile operations: SIMs are placed in vehicles that drive through the city, "
            "naturally registering on different towers. "
            "Method 3 — Antenna steering: External directional antennas on SIM boxes can register "
            "with towers farther away, distributing the load across sectors."
        ),
        threat_description=(
            "Eliminates the most basic detection signal: many SIMs concentrated on one tower. "
            "When SIMs are distributed like the real population, carrier-side anomaly detection "
            "based on tower concentration becomes ineffective."
        ),
        indicators=[
            IoC("network", "SIMs across different towers but all connected to same central infrastructure (VPN endpoint, command server)", "medium", "NetFlow / DNS logs"),
            IoC("behavioral", "SIMs at different towers show correlated activity patterns (start/stop at same times, same target recipients)", "high", "CDR cross-correlation"),
            IoC("physical", "Repeated patterns of tower handovers that don't match any known commute route (indicating antenna steering or scripted movement)", "medium", "Cell tower handover logs"),
        ],
        detection_methods=[
            DetectionMethod(
                "Cross-Tower Behavioral Correlation",
                "Even if SIMs are on different towers, they may message the same destinations, be active at the same times, or show coordinated behavior. Correlation analysis across tower-segmented data reveals hidden clusters.",
                ["CDR analytics", "Correlation engine"],
                "high", "medium", "senior",
            ),
            DetectionMethod(
                "Handover Pattern Analysis",
                "Legitimate users have predictable handover patterns (home→commute→work→commute→home). SIMs that stay on one tower 24/7 or show impossible handover sequences can be flagged.",
                ["Cell handover logs", "GIS mapping tools"],
                "medium", "medium", "mid",
            ),
        ],
        countermeasures=[
            Countermeasure("Stationary SIM Detection", "Flag SIMs that register on the same tower 24/7 for months without any handovers (real phones move).", "carrier", "medium"),
            Countermeasure("Coordinated Activity Alerts", "Cross-tower correlation engine that detects SIMs on different towers behaving identically.", "carrier", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Network coverage testing, field surveys, or distributed sensor networks for environmental monitoring.",
            legitimate_equivalent="Carrier drive-testing uses branded vehicles with carrier-issued test equipment and is coordinated with the network operations centre.",
            red_flags=[
                "No carrier coordination or drive-test reports produced",
                "SIMs are sending user traffic (SMS, social media) rather than test packets",
                "Locations are residential/commercial premises, not drive-test routes",
                "Operation continues for months rather than the typical 1–2 week test window",
            ],
            investigative_questions=[
                "Is there a drive-test or coverage survey contract with the carrier?",
                "Are the SIMs on M2M/test plans or consumer voice/SMS plans?",
                "Can the entity produce coverage maps or sensor data from the 'survey'?",
            ],
        ),
        related_ttps=["SF-T1001", "SF-T4001", "SF-T4002"],
    ),

    TTPEntry(
        id="SF-T4004",
        name="SIM Sleeping and Cycling",
        category=TTPCategory.EVASION,
        threat_level=ThreatLevel.MEDIUM,
        detection_difficulty=DetectionDifficulty.MODERATE,
        kill_chain_phase="Defense Evasion",
        summary="Rotating SIMs between active and dormant states to avoid triggering carrier rate limits and activity thresholds.",
        technical_definition=(
            "SIM sleeping is a scheduling technique where only a subset of SIMs are active at "
            "any time. Idle SIMs are deregistered from the network or placed in airplane mode. "
            "Rotation schedules (round-robin, random, or load-balanced) cycle SIMs in and out of "
            "active duty. This keeps per-SIM activity volumes within normal ranges and avoids "
            "triggering carrier thresholds for 'high-volume subscriber' alerts."
        ),
        how_it_works=(
            "The orchestration layer maintains a SIM pool with states: active, sleeping, warm-up, "
            "cooldown. A scheduler allocates SIMs to tasks. After a SIM completes its daily quota "
            "(e.g., 30 SMS), it enters cooldown (deregisters from network). Another SIM wakes from "
            "sleep and takes over. Warm-up SIMs generate background traffic before being assigned "
            "tasks. This distributes the total volume across many SIMs, keeping each individual "
            "SIM's activity below detection thresholds."
        ),
        threat_description=(
            "Prevents individual SIM-level rate alerts. Carriers set thresholds like '>100 SMS/day' "
            "to flag spam. By cycling 50 SIMs with 20 SMS each, the farm sends 1,000 SMS/day while "
            "no single SIM exceeds the threshold."
        ),
        indicators=[
            IoC("network", "Many SIMs from related ICCID ranges showing regular attach/detach cycles (e.g., 8h active, 8h off)", "medium", "HLR/VLR logs"),
            IoC("temporal", "SIM activation/deactivation patterns follow a regular schedule rather than organic user behavior", "high", "CDR time-series"),
            IoC("behavioral", "A pool of SIMs all message the same set of destinations but never simultaneously", "high", "CDR analysis"),
        ],
        detection_methods=[
            DetectionMethod(
                "Attach/Detach Cycle Analysis",
                "Monitor HLR for SIMs with regular, periodic attach/detach cycles. Real users don't power their phones on/off on a fixed schedule.",
                ["HLR/VLR logs", "Time-series analysis tools"],
                "high", "medium", "mid",
            ),
            DetectionMethod(
                "Shared Destination Analysis",
                "Identify groups of SIMs that message overlapping destination sets but are never active simultaneously — indicative of a cycling pool.",
                ["CDR database", "Set intersection algorithms"],
                "high", "low", "mid",
            ),
        ],
        countermeasures=[
            Countermeasure("Unusual Attach/Detach Rate Alerts", "Flag SIMs with more than X attach/detach events per week (threshold based on normal user distribution).", "carrier", "high"),
            Countermeasure("SIM Pool Fingerprinting", "Correlate SIMs that share ICCID batch numbers, activation dates, and destination sets — even if never simultaneously active.", "carrier", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="IoT device power management (devices sleep to conserve battery) or fleet SIM rotation for cost optimisation.",
            legitimate_equivalent="IoT power management is handled by the device firmware and doesn't show regular, synchronised attach/detach patterns across many SIMs.",
            red_flags=[
                "SIMs are on voice/SMS plans, not IoT/M2M plans",
                "Cycling schedule is synchronised across SIMs (IoT devices wake independently)",
                "SIMs send to human recipients, not IoT endpoints/MQTT brokers",
            ],
            investigative_questions=[
                "What IoT devices are these SIMs installed in? Can you provide device serial numbers?",
                "Why do the SIMs need voice/SMS capability for IoT?",
                "Can you provide the device firmware specifications showing the power management cycle?",
            ],
        ),
        related_ttps=["SF-T4001", "SF-T4002"],
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AUTOMATION — Scaling operations
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T5001",
        name="Orchestration and Command Infrastructure",
        category=TTPCategory.AUTOMATION,
        threat_level=ThreatLevel.HIGH,
        detection_difficulty=DetectionDifficulty.MODERATE,
        kill_chain_phase="Command and Control",
        summary="Centralised software controlling SIM allocation, task scheduling, account management, and content distribution.",
        technical_definition=(
            "The orchestration layer is the 'brain' of the SIM farm. It is a software system "
            "(custom-built or adapted from legitimate tools like Gammu, Kannel, n8n, or Selenium "
            "Grid) that manages: SIM inventory and state, account-to-SIM mapping, task queues "
            "(what to post, where, when), content templates and variation engines, proxy assignment, "
            "and error handling/retry logic. Communication between the orchestrator and SIM hardware "
            "uses AT commands over serial/USB or HTTP APIs."
        ),
        how_it_works=(
            "The orchestrator maintains a database of all SIMs, accounts, and proxies. Tasks "
            "(e.g., 'post this message to 50 accounts') are decomposed into atomic actions: "
            "select account → select proxy → open browser profile → navigate to platform → "
            "compose post → randomise text → post → log result. The system handles failures "
            "(account locked, proxy down) by reassigning tasks to backup resources. "
            "Content variation engines use template systems with synonym replacement, sentence "
            "reordering, and tone adjustment to make each post unique."
        ),
        threat_description=(
            "Enables a single operator to manage thousands of accounts simultaneously. Without "
            "automation, a SIM farm would require an impractical number of manual operators. "
            "The orchestration layer is what transforms hardware into a scalable operation."
        ),
        indicators=[
            IoC("network", "Central server communicating with many SIM boxes via AT-command-over-IP protocols or API calls on predictable schedules", "medium", "Network traffic analysis"),
            IoC("behavioral", "Content posted across accounts shows template-like structure with synonym variations (NLP analysis reveals common template)", "high", "Content analysis / NLP"),
            IoC("temporal", "Task execution shows machine-precision timing — actions happen at exact intervals rather than human-variable timing", "medium", "Platform action logs"),
            IoC("network", "Database queries from a central server to SIM inventory, account databases, and content template stores", "medium", "Database audit logs"),
        ],
        detection_methods=[
            DetectionMethod(
                "Content Template Detection (NLP)",
                "Apply NLP techniques (TF-IDF, sentence embeddings, n-gram analysis) across posts from suspect accounts. Template-generated content shares structural similarity even after synonym replacement. Cosine similarity > 0.7 across 'different' posts indicates templating.",
                ["NLP pipeline (spaCy, sentence-transformers)", "Content database"],
                "high", "medium", "senior",
            ),
            DetectionMethod(
                "Command Server Identification",
                "Network forensics to identify the central orchestration server. Look for a single IP/domain communicating with many SIM box IPs on modem management ports (typically 80, 443, 8080, or custom ports).",
                ["NetFlow analysis", "DNS logs", "Network forensics tools"],
                "medium", "medium", "senior",
            ),
        ],
        countermeasures=[
            Countermeasure("Content Similarity Scoring", "Platform-side NLP pipeline that scores new posts against known template structures. Flag posts with high similarity to previously identified campaign content.", "platform", "high"),
            Countermeasure("Action Timing Analysis", "Flag accounts whose action timing shows machine precision (sub-second consistency between similar actions across sessions).", "platform", "medium"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Social media management platform for agencies managing multiple client accounts, or marketing automation for legitimate campaigns.",
            legitimate_equivalent="Legitimate social media management tools (Hootsuite, Buffer, Sprout Social) use platform APIs with OAuth and comply with platform ToS. They don't require SIM cards or anti-detect browsers.",
            red_flags=[
                "Uses SIM hardware and anti-detect browsers instead of platform APIs",
                "No OAuth tokens or API keys from the platforms being managed",
                "Content is not branded or attributable to any client",
                "Accounts managed are personal profiles, not business/brand pages",
                "Scale exceeds what any legitimate agency would manage (thousands vs. dozens of accounts)",
            ],
            investigative_questions=[
                "Can the agency provide client contracts for the accounts being managed?",
                "Why does the platform require SIM cards and anti-detect browsers rather than official APIs?",
                "Are the managed accounts disclosed as agency-operated per platform Terms of Service?",
            ],
        ),
        related_ttps=["SF-T1001", "SF-T1002", "SF-T3001"],
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # AMPLIFICATION — Maximising reach and impact
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T6001",
        name="Coordinated Inauthentic Amplification",
        category=TTPCategory.AMPLIFICATION,
        threat_level=ThreatLevel.CRITICAL,
        detection_difficulty=DetectionDifficulty.HARD,
        kill_chain_phase="Impact",
        summary="Coordinated networks of fake accounts amplifying specific content through likes, shares, comments, and reposts.",
        technical_definition=(
            "Coordinated Inauthentic Amplification (CIA — distinct from the intelligence agency) "
            "is the systematic use of a network of fake accounts to boost the visibility of "
            "specific content on social media platforms. This exploits algorithmic ranking systems "
            "that promote content based on engagement signals (likes, shares, comments, saves). "
            "By generating artificial engagement, the farm pushes content into organic users' feeds."
        ),
        how_it_works=(
            "Step 1: Seed account posts the target content (political message, product review, etc.). "
            "Step 2: Within a controlled time window (staggered over 1–4 hours to appear organic), "
            "farm accounts engage with the post: like, share, comment, save. Comments are varied "
            "using template engines. "
            "Step 3: Platform algorithms detect the engagement spike and promote the post to wider "
            "audiences ('trending' or 'recommended'). "
            "Step 4: Organic users see the promoted content and generate genuine engagement, "
            "creating a positive feedback loop. "
            "Step 5: Farm accounts engage with organic users' replies to maintain conversation."
        ),
        threat_description=(
            "Manipulates the information ecosystem at scale. Political campaigns, brand "
            "manipulation, and disinformation operations all rely on this technique. The "
            "real damage comes when organic users engage with artificially promoted content "
            "without knowing it was boosted by fake accounts — manufacturing consensus."
        ),
        indicators=[
            IoC("behavioral", "Engagement burst on a post from accounts with no prior interaction history with the poster", "high", "Platform engagement logs"),
            IoC("behavioral", "Commenting accounts show low-diversity activity — they only engage with content from the same small set of accounts", "high", "Social graph analysis"),
            IoC("temporal", "Engagement arrives in a staggered but controlled window (not natural virality which follows exponential curves with sharing cascades)", "medium", "Time-series analysis of engagement"),
            IoC("behavioral", "Comment text shows template patterns: similar sentence structure with synonym variations", "high", "NLP analysis"),
        ],
        detection_methods=[
            DetectionMethod(
                "Engagement Network Graph Analysis",
                "Build a bipartite graph of accounts and content. Detect clusters of accounts that consistently engage with the same content sources. These clusters represent coordinated networks.",
                ["Graph database (Neo4j/TigerGraph)", "Community detection algorithms (Louvain, Leiden)"],
                "high", "medium", "senior",
            ),
            DetectionMethod(
                "Engagement Timing Distribution Analysis",
                "Natural viral content follows a power-law engagement curve (explosive start, long tail). Coordinated amplification shows a more uniform distribution (staggered bots). Compare engagement curves to expected viral models.",
                ["Time-series analysis", "Statistical testing"],
                "medium", "medium", "senior",
            ),
            DetectionMethod(
                "Sentiment-Content Coherence Check",
                "Comments from coordinated networks often show forced positivity or support regardless of the content's controversy level. Detect accounts that never express nuanced or negative opinions.",
                ["Sentiment analysis (VADER, BERT-based)", "Content analysis pipeline"],
                "medium", "high", "mid",
            ),
        ],
        countermeasures=[
            Countermeasure("Engagement Velocity Limits", "Rate-limit how quickly new accounts can engage with content (e.g., max 10 likes/hour for accounts <30 days old).", "platform", "medium"),
            Countermeasure("Transparency Labels", "Label content that received disproportionate engagement from new/low-trust accounts so organic users can make informed decisions.", "platform", "medium"),
            Countermeasure("CIB Takedown Programs", "Dedicated teams (like Meta's CIB program) that investigate and remove coordinated fake networks.", "platform", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Social media engagement service, community management, or fan club coordination.",
            legitimate_equivalent="Legitimate engagement services use organic growth tactics (quality content, paid promotion through platform ad systems, influencer partnerships with disclosure).",
            red_flags=[
                "Engagement comes from accounts with no organic following or activity history",
                "Accounts don't disclose paid promotion or affiliation",
                "Engagement patterns are suspiciously uniform rather than organic",
                "Service guarantees specific engagement numbers (likes, shares) — impossible with organic methods",
                "Accounts engage across unrelated topics (politics, products, celebrities) for different clients",
            ],
            investigative_questions=[
                "Are the engaging accounts real people with verifiable identities?",
                "Is the engagement disclosed as paid/sponsored per advertising standards?",
                "Can the service provider demonstrate organic audience-building methods?",
            ],
        ),
        related_ttps=["SF-T3001", "SF-T5001"],
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PERSISTENCE — Maintaining the operation long-term
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T7001",
        name="Account Recovery and Replacement Pipeline",
        category=TTPCategory.PERSISTENCE,
        threat_level=ThreatLevel.MEDIUM,
        detection_difficulty=DetectionDifficulty.MODERATE,
        kill_chain_phase="Persistence",
        summary="Automated systems to replace banned/locked accounts and maintain operational capacity.",
        technical_definition=(
            "SIM farm operations expect a percentage of accounts to be banned by platform "
            "enforcement teams. An account recovery pipeline automatically detects bans "
            "(via login failure monitoring), provisions new accounts from a pre-aged reserve "
            "pool, migrates followers/connections from the banned account's role to the "
            "replacement, and updates the orchestration system's account inventory."
        ),
        how_it_works=(
            "The pipeline maintains three account pools: "
            "1. Active — currently deployed for campaigns. "
            "2. Reserve — aged accounts ready for deployment but not yet active. "
            "3. Nursery — newly created accounts undergoing aging/warming. "
            "When an active account is banned, the system: checks the ban reason (adjusts "
            "behavior models if needed), promotes a reserve account to active, moves a nursery "
            "account to reserve, and creates a new nursery account. This maintains a steady "
            "operational capacity despite platform enforcement."
        ),
        threat_description=(
            "Makes platform enforcement a game of whack-a-mole. Even if platforms ban accounts, "
            "the farm replaces them faster than enforcement can scale. With a 50% reserve-to-active "
            "ratio, the farm can sustain 50% account losses without any reduction in output."
        ),
        indicators=[
            IoC("behavioral", "New accounts rapidly take over the exact social graph and posting patterns of recently banned accounts", "high", "Platform account lifecycle analysis"),
            IoC("temporal", "Replacement accounts become active within hours of the original's ban — faster than organic account creation", "high", "Account creation vs. ban timing"),
            IoC("behavioral", "Reserve pool accounts show identical aging patterns (same types of content, same timing, same interest groups)", "medium", "Cross-account behavioral analysis"),
        ],
        detection_methods=[
            DetectionMethod(
                "Account Succession Analysis",
                "Track banned accounts' social graphs (followers, group memberships, interaction partners). When a new account appears and rapidly assumes the same graph position, flag it as a potential replacement.",
                ["Social graph database", "Graph similarity algorithms"],
                "high", "medium", "senior",
            ),
            DetectionMethod(
                "Nursery Pool Detection",
                "Identify clusters of recently created accounts undergoing similar aging patterns (same content types, same interaction targets). These represent the nursery pool of a SIM farm.",
                ["Account creation analytics", "Behavioral clustering"],
                "medium", "medium", "mid",
            ),
        ],
        countermeasures=[
            Countermeasure("Social Graph Inheritance Blocking", "When banning an account, also flag accounts that rapidly assume its social graph position.", "platform", "high"),
            Countermeasure("Ban Evasion Detection", "Link accounts by device/browser fingerprint, IP, and behavioral patterns to detect the same operator creating replacement accounts.", "platform", "high"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Backup accounts for business continuity, or managing account transitions when employees leave.",
            legitimate_equivalent="Legitimate businesses use platform Business Manager tools for account ownership transfer and have documented employee transitions.",
            red_flags=[
                "Replacement accounts appear within hours, not through a normal HR process",
                "The 'employees' leaving don't appear in any HR records",
                "Multiple replacement accounts exist for a single 'departed employee'",
                "Replacement accounts immediately resume the exact posting cadence of the original",
            ],
            investigative_questions=[
                "Can the business document the employee transitions for each account change?",
                "Why does the business maintain a reserve pool of pre-created accounts?",
                "Are the account transitions handled through the platform's official business tools?",
            ],
        ),
        related_ttps=["SF-T3001", "SF-T5001"],
    ),

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # EXFILTRATION — Extracting value
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    TTPEntry(
        id="SF-T8001",
        name="OTP Harvesting and Account Takeover",
        category=TTPCategory.EXFILTRATION,
        threat_level=ThreatLevel.CRITICAL,
        detection_difficulty=DetectionDifficulty.MODERATE,
        kill_chain_phase="Collection",
        summary="Intercepting one-time passwords (OTPs) delivered via SMS to SIM farm numbers for account verification or takeover.",
        technical_definition=(
            "OTP harvesting uses the farm's SIM cards to receive SMS-based verification codes. "
            "This enables: (1) Creating accounts on platforms that require phone verification, "
            "(2) Bypassing 2FA on compromised accounts (if the attacker controls the recovery "
            "phone number), (3) Selling 'phone verified accounts' (PVAs) on underground markets."
        ),
        how_it_works=(
            "The orchestration system registers a SIM's phone number on a target platform. "
            "The platform sends an OTP via SMS. The SIM box's AT interface reads the incoming SMS "
            "(AT+CMGR), extracts the OTP via regex, and forwards it to the orchestrator. "
            "The orchestrator enters the OTP on the platform within the validity window "
            "(typically 60–300 seconds). After verification, the SIM may be recycled for another "
            "platform. Some operators sell OTP-receiving capacity as a service (SMSActivate, "
            "5SIM, TextVerified) — these are commercial fronts for SIM farms."
        ),
        threat_description=(
            "Undermines SMS-based authentication — the most widely deployed 2FA method globally. "
            "Enables mass creation of fake accounts on any platform using SMS verification, and "
            "can facilitate account takeover when combined with phishing."
        ),
        indicators=[
            IoC("behavioral", "SIMs that only receive SMS but never send (or send only to platform verification numbers)", "high", "CDR analysis"),
            IoC("temporal", "SMS received is always from shortcodes/platform sender IDs (e.g., 'Google', 'Facebook', 'Twitter'), never personal contacts", "high", "CDR content analysis (where legal)"),
            IoC("behavioral", "Very short SIM active periods — SIM activates, receives 1–3 SMS within minutes, then goes dormant", "high", "CDR + HLR logs"),
            IoC("financial", "Revenue from selling 'phone verified accounts' or 'OTP services' online", "medium", "Financial records / OSINT"),
        ],
        detection_methods=[
            DetectionMethod(
                "OTP-Only Traffic Profiling",
                "Identify SIMs whose traffic consists almost exclusively of receiving SMS from known OTP sender IDs (shortcodes, platform names). These SIMs are being used for verification farming.",
                ["CDR database", "Known OTP sender ID list"],
                "high", "low", "junior",
            ),
            DetectionMethod(
                "Ephemeral SIM Detection",
                "Flag SIMs with very short active windows — active for minutes, dormant for days. Cross-reference with platform account creation spikes.",
                ["HLR logs", "CDR time-series"],
                "high", "low", "mid",
            ),
        ],
        countermeasures=[
            Countermeasure("Deprecate SMS-Based 2FA", "Move to app-based TOTP, push notifications, or hardware keys (FIDO2/WebAuthn) instead of SMS OTPs.", "platform", "high"),
            Countermeasure("Phone Number Reputation Scoring", "Score phone numbers based on age, carrier type, usage patterns before accepting them for verification.", "platform", "medium"),
            Countermeasure("VoIP/Virtual Number Blocking", "Block verification to known VoIP ranges, virtual numbers, and numbers flagged by carrier intelligence.", "platform", "medium"),
        ],
        ethical_cover=EthicalCover(
            claimed_purpose="Testing platform security by verifying how easily accounts can be created, or providing virtual number services for privacy.",
            legitimate_equivalent="Legitimate security testing is conducted under authorised penetration test agreements with the platform. Privacy-focused virtual number services (Google Voice, etc.) are platform-operated.",
            red_flags=[
                "No penetration test agreement or bug bounty program participation",
                "Scale far exceeds any legitimate testing scope (thousands of verifications)",
                "Verified accounts are sold or used rather than reported as test findings",
                "Service is advertised on underground forums or grey-market websites",
            ],
            investigative_questions=[
                "Is there an authorised security testing agreement with the platforms being verified against?",
                "What happens to the accounts after 'testing' — are they deleted or used?",
                "Are test results documented and reported to the platform's security team?",
            ],
        ),
        related_ttps=["SF-T2001", "SF-T3001", "SF-T5001"],
    ),
]


def get_all_ttps() -> list[dict]:
    """Return all TTPs as serialisable dicts."""
    results = []
    for ttp in TTP_DATABASE:
        results.append({
            "id": ttp.id,
            "name": ttp.name,
            "category": ttp.category.value,
            "threat_level": ttp.threat_level.value,
            "detection_difficulty": ttp.detection_difficulty.value,
            "kill_chain_phase": ttp.kill_chain_phase,
            "summary": ttp.summary,
            "technical_definition": ttp.technical_definition,
            "how_it_works": ttp.how_it_works,
            "threat_description": ttp.threat_description,
            "indicators": [
                {"type": i.indicator_type, "description": i.description,
                 "confidence": i.detection_confidence, "data_source": i.data_source}
                for i in ttp.indicators
            ],
            "detection_methods": [
                {"name": d.name, "description": d.description,
                 "tools": d.tools_required, "effectiveness": d.effectiveness,
                 "false_positive_rate": d.false_positive_rate,
                 "skill_level": d.skill_level_required}
                for d in ttp.detection_methods
            ],
            "countermeasures": [
                {"name": c.name, "description": c.description,
                 "level": c.implementation_level, "effectiveness": c.effectiveness}
                for c in ttp.countermeasures
            ],
            "ethical_cover": {
                "claimed_purpose": ttp.ethical_cover.claimed_purpose,
                "legitimate_equivalent": ttp.ethical_cover.legitimate_equivalent,
                "red_flags": ttp.ethical_cover.red_flags,
                "investigative_questions": ttp.ethical_cover.investigative_questions,
            } if ttp.ethical_cover else None,
            "related_ttps": ttp.related_ttps,
            "real_world_examples": ttp.real_world_examples,
        })
    return results


def get_ttp_by_id(ttp_id: str) -> dict | None:
    """Get a single TTP by ID."""
    for ttp in TTP_DATABASE:
        if ttp.id == ttp_id:
            return get_all_ttps()[TTP_DATABASE.index(ttp)]
    return None


def get_ttps_by_category(category: str) -> list[dict]:
    """Get TTPs filtered by category."""
    all_ttps = get_all_ttps()
    return [t for t in all_ttps if t["category"] == category]


def get_categories() -> list[dict]:
    """Get all TTP categories with counts."""
    cat_counts: dict[str, int] = {}
    for ttp in TTP_DATABASE:
        cat_counts[ttp.category.value] = cat_counts.get(ttp.category.value, 0) + 1
    cat_names = {
        "infrastructure": "Infrastructure",
        "acquisition": "SIM Acquisition",
        "identity": "Identity & Personas",
        "evasion": "Detection Evasion",
        "automation": "Automation & C2",
        "amplification": "Amplification & Impact",
        "persistence": "Persistence",
        "exfiltration": "Exfiltration & Monetisation",
    }
    return [
        {"id": cat, "name": cat_names.get(cat, cat.title()), "count": count}
        for cat, count in cat_counts.items()
    ]
