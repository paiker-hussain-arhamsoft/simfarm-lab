"""Detection Scenarios — Forensic investigation exercises for the Legendary module.

Each scenario presents students with realistic data artifacts from an advanced SIM farm
and asks them to identify the indicators, determine the technique being used, and
recommend countermeasures.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field


@dataclass
class ScenarioEvidence:
    """A piece of evidence within a scenario."""
    evidence_type: str  # cdr_log, hlr_record, netflow, financial, social_graph, content_sample
    title: str
    description: str
    data: dict | list  # Structured data for the evidence


@dataclass
class ScenarioQuestion:
    """A question within a scenario."""
    id: str
    question: str
    question_type: str  # multiple_choice, free_text, flag
    options: list[str] | None = None
    correct_answer: str = ""
    explanation: str = ""
    points: int = 10
    hint: str = ""


@dataclass
class DetectionScenario:
    """A complete investigation scenario."""
    id: str
    title: str
    difficulty: str  # intermediate, advanced, expert
    category: str  # maps to TTP category
    related_ttps: list[str]
    briefing: str
    context: str
    evidence: list[ScenarioEvidence]
    questions: list[ScenarioQuestion]
    total_points: int = 0
    time_estimate_minutes: int = 30
    skills_tested: list[str] = field(default_factory=list)


# ────────────────────────────────────────────────────────────────────
# SCENARIOS
# ────────────────────────────────────────────────────────────────────

SCENARIOS: list[DetectionScenario] = [

    DetectionScenario(
        id="DS-001",
        title="The Silent Chorus",
        difficulty="intermediate",
        category="amplification",
        related_ttps=["SF-T6001", "SF-T3001", "SF-T4002"],
        briefing=(
            "A local council election candidate has reported suspicious activity on their "
            "social media posts. Over the past 2 weeks, their opponent's posts have received "
            "an unusual spike in engagement — hundreds of likes and supportive comments within "
            "hours of posting, while the candidate's content remains at normal levels."
        ),
        context=(
            "You are an analyst at the Electoral Commission's Digital Intelligence Unit. "
            "You have been provided with platform engagement data, account metadata, and "
            "CDR records from a carrier cooperation request. Your task: determine if this "
            "is coordinated inauthentic amplification and identify the indicators."
        ),
        evidence=[
            ScenarioEvidence(
                evidence_type="social_graph",
                title="Engagement Pattern Data (48 hours)",
                description="Engagement events on the opponent's top 5 posts over 48 hours.",
                data={
                    "posts": [
                        {"post_id": "P-4491", "posted_at": "2026-03-15T09:22:00Z",
                         "organic_likes_0_1h": 12, "suspect_likes_1_2h": 147,
                         "suspect_comments_1_2h": 34, "organic_engagement_after_24h": 891},
                        {"post_id": "P-4495", "posted_at": "2026-03-15T14:05:00Z",
                         "organic_likes_0_1h": 8, "suspect_likes_1_2h": 163,
                         "suspect_comments_1_2h": 41, "organic_engagement_after_24h": 1203},
                        {"post_id": "P-4502", "posted_at": "2026-03-16T08:45:00Z",
                         "organic_likes_0_1h": 15, "suspect_likes_1_2h": 122,
                         "suspect_comments_1_2h": 28, "organic_engagement_after_24h": 756},
                    ],
                    "engagement_window": "Suspect engagement consistently arrives 60-120 min after posting",
                    "stagger_pattern": "3.2s average interval between engagements (±0.8s std dev)",
                },
            ),
            ScenarioEvidence(
                evidence_type="content_sample",
                title="Sample Comments from Suspect Accounts",
                description="Representative comments posted by the suspect account cluster.",
                data={
                    "comments": [
                        {"account": "LocalMum_Sarah82", "text": "Finally someone speaking sense! Been saying this for years about our high street."},
                        {"account": "DaveFromBristol_", "text": "At last someone who talks sense! Have been saying this for ages about our town centre."},
                        {"account": "JennyW_Cardiff", "text": "Finally a candidate who speaks sense! I've been saying this for years about our local area."},
                        {"account": "MarkT_Newport", "text": "About time someone speaks sense! Have said this for years about our neighbourhood."},
                        {"account": "SueB_Swansea99", "text": "At last someone talking sense! Been thinking this for ages about our community."},
                    ],
                    "similarity_note": "NLP analysis shows cosine similarity > 0.82 across all comments (template with synonym substitution)",
                },
            ),
            ScenarioEvidence(
                evidence_type="cdr_log",
                title="CDR Extract — SIMs Linked to Suspect Account Phone Numbers",
                description="Phone numbers used to register the suspect accounts — CDR analysis.",
                data={
                    "sim_count": 47,
                    "carrier_distribution": {"giffgaff": 19, "Lycamobile": 15, "Lebara": 13},
                    "activation_window": "All activated within 2026-01-05 to 2026-01-19 (14 days)",
                    "cell_tower_distribution": {
                        "TWR-Bristol-001": 8, "TWR-Bristol-004": 7, "TWR-Cardiff-002": 6,
                        "TWR-Newport-001": 5, "TWR-Swansea-003": 5, "TWR-Bristol-009": 4,
                        "various_others": 12,
                    },
                    "traffic_profile": "91% of traffic is data-only (no voice, minimal SMS beyond OTP receipt)",
                    "imei_note": "34 of 47 SIMs share the same TAC prefix (35332510) — GSM modem chipset",
                },
            ),
        ],
        questions=[
            ScenarioQuestion(
                id="DS-001-Q1",
                question="What is the primary indicator that the engagement is coordinated rather than organic?",
                question_type="multiple_choice",
                options=[
                    "The high volume of engagement",
                    "The consistent 60-120 minute delay and 3.2s average interval between engagements",
                    "The positive sentiment of comments",
                    "The accounts using Welsh city names",
                ],
                correct_answer="The consistent 60-120 minute delay and 3.2s average interval between engagements",
                explanation="Organic viral content shows exponential engagement curves with variable timing. The consistent delay window and machine-precision 3.2s intervals indicate automated scheduling.",
                points=10,
            ),
            ScenarioQuestion(
                id="DS-001-Q2",
                question="Identify the content generation technique being used based on the comment samples.",
                question_type="multiple_choice",
                options=[
                    "Manual writing by multiple authors",
                    "Template-based generation with synonym substitution",
                    "Large Language Model (ChatGPT-style) generation",
                    "Copy-paste from a script",
                ],
                correct_answer="Template-based generation with synonym substitution",
                explanation="The comments share identical sentence structure ('Finally/At last someone [verb] sense! [Been/Have been] [saying/thinking] this for [years/ages] about our [local noun].'). This is a template with controlled synonym swap — not LLM-generated (which would show more structural variation) or manual (which would show more diversity).",
                points=10,
            ),
            ScenarioQuestion(
                id="DS-001-Q3",
                question="What does the CDR data tell you about the infrastructure? Identify the most damning indicator.",
                question_type="multiple_choice",
                options=[
                    "SIMs are on cheap carriers",
                    "SIMs activated in a 14-day window",
                    "34 of 47 SIMs share the same TAC prefix (35332510) — identical GSM modem hardware",
                    "SIMs distributed across Welsh cities",
                ],
                correct_answer="34 of 47 SIMs share the same TAC prefix (35332510) — identical GSM modem hardware",
                explanation="The TAC (Type Allocation Code) identifies the device model. 72% of SIMs appearing in the same GSM modem chipset (despite claiming to be different 'local' users) is conclusive evidence of a SIM box deployment. Real users have diverse devices.",
                points=15,
            ),
            ScenarioQuestion(
                id="DS-001-Q4",
                question="What TTP category best describes the overall operation?",
                question_type="multiple_choice",
                options=[
                    "SF-T6001: Coordinated Inauthentic Amplification",
                    "SF-T8001: OTP Harvesting",
                    "SF-T4001: IMEI/IMSI Rotation",
                    "SF-T1003: Residential Proxy Infrastructure",
                ],
                correct_answer="SF-T6001: Coordinated Inauthentic Amplification",
                explanation="The operation is using fake accounts to boost engagement on a political candidate's posts — textbook coordinated inauthentic amplification for electoral manipulation.",
                points=10,
            ),
            ScenarioQuestion(
                id="DS-001-Q5",
                question="What three countermeasures would you recommend to the platform?",
                question_type="free_text",
                correct_answer="engagement_velocity_limits|content_similarity_scoring|cib_takedown",
                explanation="Key countermeasures: (1) Engagement velocity limits for new/low-trust accounts, (2) NLP-based content similarity scoring to detect template comments, (3) CIB investigation and network takedown. Additional measures: TAC-based device diversity requirements for account creation.",
                points=20,
                hint="Think about rate limits, content analysis, and network-level enforcement.",
            ),
        ],
        total_points=65,
        time_estimate_minutes=25,
        skills_tested=["CDR analysis", "NLP/content forensics", "Social graph analysis", "Countermeasure design"],
    ),

    DetectionScenario(
        id="DS-002",
        title="The Ghost in the Machine",
        difficulty="advanced",
        category="evasion",
        related_ttps=["SF-T4002", "SF-T4001", "SF-T4003", "SF-T4004"],
        briefing=(
            "Your carrier's fraud analytics system has been consistently clean for 6 months. "
            "However, an anonymous tip (from a disgruntled former employee of a 'marketing agency') "
            "claims that a SIM farm of ~200 SIMs has been operating in the Manchester area for "
            "over a year — completely undetected by your systems. The tipster provided one phone "
            "number from the farm. Your job: use that thread to unravel the network."
        ),
        context=(
            "You are a senior analyst at a UK mobile carrier's fraud investigation unit. "
            "You have full access to CDR data, HLR/EIR records, and cell tower logs. "
            "The tipster's number: +447911234567. Find the rest of the farm."
        ),
        evidence=[
            ScenarioEvidence(
                evidence_type="cdr_log",
                title="CDR Profile — Tipster's Number (+447911234567)",
                description="30-day CDR extract for the known farm SIM.",
                data={
                    "msisdn": "+447911234567",
                    "daily_sms_avg": 8.3,
                    "daily_voice_minutes_avg": 12.7,
                    "daily_data_mb_avg": 847,
                    "active_hours": "07:00-23:00 (typical professional pattern)",
                    "cell_towers_used": ["TWR-MCR-014", "TWR-MCR-022", "TWR-MCR-031"],
                    "tower_pattern": "TWR-MCR-014 (evenings/weekends), TWR-MCR-022 (weekdays 9-17), TWR-MCR-031 (commute hours)",
                    "imei": "356789012345678",
                    "imei_tac": "35678901 (Samsung Galaxy S24)",
                    "ip_address": "86.12.47.193 (Virgin Media residential)",
                    "assessment": "PASSES all standard fraud checks — looks like a normal professional user",
                },
            ),
            ScenarioEvidence(
                evidence_type="hlr_record",
                title="EIR Analysis — IMEI History",
                description="IMEI change history for the tipster's SIM over 12 months.",
                data={
                    "imei_changes": [
                        {"date": "2025-04-01", "imei": "352345678901234", "tac_model": "iPhone 14 Pro"},
                        {"date": "2025-06-15", "imei": "354567890123456", "tac_model": "Samsung Galaxy S23"},
                        {"date": "2025-09-01", "imei": "356789012345678", "tac_model": "Samsung Galaxy S24"},
                    ],
                    "normal_rate": "1.2 device changes per year for general population",
                    "this_sim_rate": "3 changes in 12 months",
                    "note": "Each change coincides with a popular phone launch date — appears organic at first glance",
                },
            ),
            ScenarioEvidence(
                evidence_type="netflow",
                title="Network Analysis — Correlated Activity",
                description="Cross-referencing the tipster's SIM with other SIMs on the same towers.",
                data={
                    "total_sims_on_same_towers": 14273,
                    "sims_with_similar_traffic_profile": 892,
                    "sims_with_correlated_active_periods": 47,
                    "correlation_method": "Pearson correlation of hourly activity vectors (r > 0.85)",
                    "correlated_sims_carrier_mix": {"EE": 12, "Three": 11, "giffgaff": 10, "Vodafone": 8, "Lycamobile": 6},
                    "correlated_sims_tower_distribution": "Distributed across 15 different towers in Greater Manchester",
                    "correlated_sims_imei_analysis": "All unique TACs — no shared hardware indicator",
                    "key_finding": "Despite perfect individual profiles, 47 SIMs show r=0.87 correlation in activity onset/offset times (within ±3 minutes daily)",
                },
            ),
            ScenarioEvidence(
                evidence_type="cdr_log",
                title="Fleet-Level Statistical Anomaly",
                description="Aggregate statistics for the 47 correlated SIMs vs. general population baseline.",
                data={
                    "metric_comparisons": [
                        {"metric": "Emergency calls (999/112) in 12 months", "fleet_47": 0, "population_baseline": "2.1 per person per year"},
                        {"metric": "International roaming events", "fleet_47": 0, "population_baseline": "1.4 trips per year"},
                        {"metric": "SIM-in-new-device events", "fleet_47": "2.8/year avg", "population_baseline": "1.2/year avg"},
                        {"metric": "KS-test p-value (inter-message timing vs Poisson)", "fleet_47": "p=0.97", "population_baseline": "p=0.34 (real users are messy)"},
                        {"metric": "Distinct persona archetypes in fleet", "fleet_47": 7, "population_baseline": "N/A (continuous distribution)"},
                    ],
                },
            ),
        ],
        questions=[
            ScenarioQuestion(
                id="DS-002-Q1",
                question="The tipster's SIM passes all standard fraud checks. What is the first technique you would use to find related farm SIMs?",
                question_type="multiple_choice",
                options=[
                    "Check for shared IP addresses",
                    "Cross-tower activity correlation (temporal analysis)",
                    "IMEI TAC matching",
                    "Check for bulk SIM purchases",
                ],
                correct_answer="Cross-tower activity correlation (temporal analysis)",
                explanation="Since individual SIMs pass all checks, you need fleet-level analysis. Activity correlation (when SIMs wake up and go dormant together) reveals that despite being on different towers with different IMEIs, a group of SIMs share the same orchestration clock.",
                points=15,
            ),
            ScenarioQuestion(
                id="DS-002-Q2",
                question="What does the KS-test p-value of 0.97 tell you about the fleet's traffic?",
                question_type="multiple_choice",
                options=[
                    "The traffic is highly irregular — likely human",
                    "The traffic fits a Poisson distribution too perfectly — likely synthetic/generated",
                    "The traffic is identical across all SIMs",
                    "The SIMs are malfunctioning",
                ],
                correct_answer="The traffic fits a Poisson distribution too perfectly — likely synthetic/generated",
                explanation="Real human behavior is messy — it doesn't conform to neat statistical models. A p=0.97 means the traffic fits a Poisson process almost perfectly, which is a sign it was GENERATED from a Poisson model. Real users typically show p=0.3-0.5 (significant deviation from any single model).",
                points=20,
            ),
            ScenarioQuestion(
                id="DS-002-Q3",
                question="The fleet has zero emergency calls and zero roaming in 12 months. Why is this significant?",
                question_type="free_text",
                correct_answer="statistical_impossibility|real_population_baseline",
                explanation="Any real population of 47 people will statistically make ~99 emergency calls and have ~66 roaming events per year. ZERO across the entire fleet in 12 months is statistically near-impossible (p < 0.001) for a real population. This indicates the SIMs are not used by real people living real lives.",
                points=15,
                hint="Think about what real people do that SIM farm personas can't simulate.",
            ),
            ScenarioQuestion(
                id="DS-002-Q4",
                question="What evasion technique explains why IMEI changes look organic (coinciding with phone launches)?",
                question_type="multiple_choice",
                options=[
                    "The operator is actually buying new phones",
                    "IMEI rotation timed to match real product launch dates to appear as legitimate upgrades (SF-T4001)",
                    "The carrier's EIR is malfunctioning",
                    "The SIMs are being physically moved between phones",
                ],
                correct_answer="IMEI rotation timed to match real product launch dates to appear as legitimate upgrades (SF-T4001)",
                explanation="This is sophisticated IMEI rotation (SF-T4001) where the operator changes IMEIs to match recently launched devices at times when legitimate users would also be upgrading. This makes each individual change look organic, but the fleet-wide pattern (ALL SIMs 'upgrading' at exactly the launch date) is the giveaway.",
                points=15,
            ),
            ScenarioQuestion(
                id="DS-002-Q5",
                question="You've identified 47 correlated SIMs, but the tipster claimed ~200. What technique would you use to find the remaining SIMs that don't correlate with this cluster?",
                question_type="free_text",
                correct_answer="persona_archetype_clustering|destination_correlation|financial_investigation",
                explanation="The remaining SIMs may be in different orchestration groups (different schedules). Approaches: (1) Cluster by persona archetype — the fleet shows exactly 7 archetypes, look for other SIMs matching these same 7 profiles. (2) Destination correlation — do any SIMs outside the 47 message the same unusual destination numbers? (3) Financial investigation — trace the payment/purchase records for the 47 identified SIMs back to the buyer and find other purchases.",
                points=25,
                hint="Consider that the farm may operate in multiple independently-scheduled clusters.",
            ),
        ],
        total_points=90,
        time_estimate_minutes=45,
        skills_tested=["Statistical analysis", "Fleet-level anomaly detection", "Correlation analysis", "Investigation methodology"],
    ),

    DetectionScenario(
        id="DS-003",
        title="The Ethical Facade",
        difficulty="expert",
        category="ethical_cover",
        related_ttps=["SF-T1002", "SF-T3001", "SF-T5001", "SF-T6001"],
        briefing=(
            "A company called 'TrueReach Digital Ltd' has been identified as potentially operating "
            "a large-scale SIM farm. They claim to be a 'social media marketing agency' specialising "
            "in 'organic growth strategies'. You have been asked to assess whether their operations "
            "are legitimate or a front for coordinated inauthentic behavior."
        ),
        context=(
            "You are a digital forensics investigator working with the Information Commissioner's "
            "Office (ICO). You have obtained business records, platform data, and network intelligence "
            "under a warrant. Assess the evidence and determine whether the 'ethical cover' holds up."
        ),
        evidence=[
            ScenarioEvidence(
                evidence_type="financial",
                title="Company Records — TrueReach Digital Ltd",
                description="Companies House filings and financial records.",
                data={
                    "company_number": "14523891",
                    "incorporated": "2024-08-15",
                    "registered_address": "Unit 7, Riverside Business Park, Manchester, M3 4FN",
                    "directors": ["James A. Wilson (DOB 1991)", "Priya K. Sharma (DOB 1989)"],
                    "declared_activity": "SIC 73110 — Advertising agencies",
                    "annual_revenue_declared": "£287,000",
                    "expenses_of_note": [
                        {"item": "Bright Data subscription", "amount": "£14,400/year", "category": "Software"},
                        {"item": "GoLogin Pro (500 profiles)", "amount": "£3,600/year", "category": "Software"},
                        {"item": "Bulk SIM purchases (giffgaff, Lycamobile)", "amount": "£8,200/year", "category": "Hardware"},
                        {"item": "Samsung Galaxy A14 x120", "amount": "£18,000", "category": "Hardware"},
                        {"item": "Multi-port USB hubs x6", "amount": "£1,200", "category": "Hardware"},
                    ],
                    "client_contracts_on_file": 3,
                    "client_revenue": "£42,000 (15% of total revenue)",
                    "unattributed_revenue": "£245,000 (85% of total revenue — source unclear)",
                },
            ),
            ScenarioEvidence(
                evidence_type="content_sample",
                title="TrueReach's Public Claims vs Reality",
                description="Their website claims vs observed operations.",
                data={
                    "website_claims": [
                        "We help businesses grow their social media presence organically",
                        "Our team of 15 social media managers create authentic engagement",
                        "We use data-driven strategies, not bots or fake accounts",
                        "Trusted by 50+ brands across the UK",
                    ],
                    "observed_reality": [
                        "No employees on PAYE beyond the 2 directors",
                        "120 Android phones found on premises during inspection",
                        "500 anti-detect browser profiles (GoLogin) running on 3 workstations",
                        "Only 3 client contracts on file (not 50+)",
                        "85% of revenue is unattributed to any client",
                        "Bright Data residential proxy subscription active",
                        "Phone farm devices running Instagram, TikTok, Facebook, X simultaneously",
                    ],
                },
            ),
            ScenarioEvidence(
                evidence_type="social_graph",
                title="Account Network Analysis",
                description="Platform data from cooperation request showing TrueReach-linked accounts.",
                data={
                    "accounts_identified": 2847,
                    "platforms": {"Instagram": 1205, "TikTok": 892, "Facebook": 450, "X/Twitter": 300},
                    "account_age_distribution": "73% created 6-12 months ago, 20% created 3-6 months ago, 7% created <3 months ago",
                    "content_categories": {
                        "political_uk": "34% — UK political commentary, candidate support",
                        "product_reviews": "28% — fake product reviews (electronics, supplements)",
                        "generic_lifestyle": "38% — aging/warming content (food, pets, travel)",
                    },
                    "engagement_patterns": "Accounts engage with each other in coordinated clusters of 30-50",
                    "phone_verification": "All accounts verified with UK mobile numbers from giffgaff/Lycamobile/Lebara",
                },
            ),
        ],
        questions=[
            ScenarioQuestion(
                id="DS-003-Q1",
                question="List 3 specific red flags that distinguish TrueReach from a legitimate social media agency.",
                question_type="free_text",
                correct_answer="no_employees|phone_farm_hardware|unattributed_revenue|anti_detect_browsers|bulk_sims",
                explanation="Key red flags: (1) No employees beyond directors — a '15-person team' with 0 PAYE records; (2) Physical phone farm hardware (120 phones + USB hubs) — legitimate agencies use platform APIs; (3) 85% unattributed revenue — legitimate agencies can attribute all revenue to client contracts; (4) Anti-detect browsers — no legitimate use case for a marketing agency; (5) Bulk SIM purchases — legitimate agencies don't need thousands of phone numbers.",
                points=20,
                hint="Compare their claimed business model to what legitimate agencies actually do.",
            ),
            ScenarioQuestion(
                id="DS-003-Q2",
                question="What is the significance of the Bright Data subscription in the context of their operations?",
                question_type="multiple_choice",
                options=[
                    "It's a normal business tool for market research",
                    "It provides residential proxies to make 2847 accounts appear to be from different locations (SF-T1003)",
                    "It's used for competitor analysis",
                    "It's for website performance monitoring",
                ],
                correct_answer="It provides residential proxies to make 2847 accounts appear to be from different locations (SF-T1003)",
                explanation="Bright Data is a residential proxy provider. In the context of running 2847 fake accounts with anti-detect browsers, it provides unique residential IPs per account to defeat platform IP-based detection. This is SF-T1003 (Residential Proxy Infrastructure).",
                points=15,
            ),
            ScenarioQuestion(
                id="DS-003-Q3",
                question="34% of the account network is engaged in UK political commentary. Under which UK legislation could this constitute a criminal offence?",
                question_type="multiple_choice",
                options=[
                    "Data Protection Act 2018 only",
                    "Online Safety Act 2023, Computer Misuse Act 1990, and potentially Representation of the People Act 1983 (if during election period)",
                    "Telecommunications Act 1984 only",
                    "Consumer Rights Act 2015",
                ],
                correct_answer="Online Safety Act 2023, Computer Misuse Act 1990, and potentially Representation of the People Act 1983 (if during election period)",
                explanation="Online Safety Act 2023: platforms must address coordinated inauthentic behavior; Computer Misuse Act 1990: unauthorised access/use of computer systems (fake accounts violate platform ToS); Representation of the People Act 1983: undisclosed campaign expenditure during election periods. If the accounts promote candidates without declaration, it's also an Electoral Commission offence.",
                points=15,
            ),
            ScenarioQuestion(
                id="DS-003-Q4",
                question="How would you determine who is PAYING TrueReach for the political commentary accounts (the 85% unattributed revenue)?",
                question_type="free_text",
                correct_answer="financial_investigation|bank_records|cryptocurrency|client_communication",
                explanation="Investigation approach: (1) Bank records subpoena — trace incoming payments to source accounts; (2) Communication records — email/messaging between directors and political clients; (3) Cryptocurrency analysis if payments are in crypto; (4) Platform ad spend correlation — cross-reference political content topics with entities that benefit; (5) Analyse the content itself — which candidates/parties benefit from the 34% political content.",
                points=25,
                hint="Follow the money and the beneficiaries.",
            ),
            ScenarioQuestion(
                id="DS-003-Q5",
                question="TrueReach's lawyers argue their operation is 'social media management, which is legal.' Write 3 investigative questions that pierce this ethical cover.",
                question_type="free_text",
                correct_answer="identity_disclosure|consent|platform_tos|client_contracts",
                explanation="Piercing questions: (1) 'If these are managed accounts, can you identify the real person or brand behind each of the 2847 accounts? Legitimate management is always disclosed.' (2) 'Can you produce signed client contracts and consent for every account being managed? Only 3 contracts exist for 2847 accounts.' (3) 'Why do you need anti-detect browsers and residential proxies if you're doing legitimate marketing? Legitimate agencies use platform-approved APIs.' (4) 'Are any of these accounts identified as managed/sponsored accounts per ASA/FTC guidelines? None are.'",
                points=25,
                hint="Focus on: disclosure, consent, tooling justification, and regulatory compliance.",
            ),
        ],
        total_points=100,
        time_estimate_minutes=60,
        skills_tested=["Financial forensics", "Legal framework knowledge", "Ethical cover analysis", "Investigation methodology"],
    ),
]


def get_all_scenarios() -> list[dict]:
    """Return all scenarios as serialisable dicts."""
    results = []
    for s in SCENARIOS:
        results.append({
            "id": s.id,
            "title": s.title,
            "difficulty": s.difficulty,
            "category": s.category,
            "related_ttps": s.related_ttps,
            "briefing": s.briefing,
            "context": s.context,
            "total_points": s.total_points,
            "time_estimate_minutes": s.time_estimate_minutes,
            "skills_tested": s.skills_tested,
            "question_count": len(s.questions),
            "evidence_count": len(s.evidence),
        })
    return results


def get_scenario_detail(scenario_id: str) -> dict | None:
    """Get full scenario with evidence and questions."""
    for s in SCENARIOS:
        if s.id == scenario_id:
            return {
                "id": s.id,
                "title": s.title,
                "difficulty": s.difficulty,
                "category": s.category,
                "related_ttps": s.related_ttps,
                "briefing": s.briefing,
                "context": s.context,
                "total_points": s.total_points,
                "time_estimate_minutes": s.time_estimate_minutes,
                "skills_tested": s.skills_tested,
                "evidence": [
                    {"type": e.evidence_type, "title": e.title,
                     "description": e.description, "data": e.data}
                    for e in s.evidence
                ],
                "questions": [
                    {"id": q.id, "question": q.question, "type": q.question_type,
                     "options": q.options, "points": q.points, "hint": q.hint}
                    for q in s.questions
                ],
            }
    return None


def check_answer(scenario_id: str, question_id: str, answer: str) -> dict:
    """Check a student's answer against the correct answer."""
    for s in SCENARIOS:
        if s.id == scenario_id:
            for q in s.questions:
                if q.id == question_id:
                    if q.question_type == "multiple_choice":
                        correct = answer.strip() == q.correct_answer.strip()
                    else:
                        # Free text: check if answer contains key concepts
                        keywords = q.correct_answer.split("|")
                        matched = sum(1 for kw in keywords if kw.lower() in answer.lower())
                        correct = matched >= len(keywords) * 0.6  # 60% keyword match
                    return {
                        "correct": correct,
                        "points_earned": q.points if correct else 0,
                        "max_points": q.points,
                        "explanation": q.explanation,
                        "correct_answer": q.correct_answer if not correct else None,
                    }
    return {"error": "Question not found"}
