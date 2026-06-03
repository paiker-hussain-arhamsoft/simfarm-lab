"""Detection exercises for each difficulty level."""

from __future__ import annotations

from backend.simulator.models import Exercise, Level

BEGINNER_EXERCISES = [
    Exercise(
        exercise_id="beginner-01",
        level=Level.BEGINNER,
        title="Identify the SIM Farm Tower",
        description=(
            "Analyze the SIM registration data. Which cell tower has an "
            "abnormally high number of SIM cards registered?"
        ),
        objective="Find the tower ID hosting the SIM farm.",
        hints=[
            "Count SIMs per cell tower — one tower will stand out immediately.",
            "Legitimate towers typically serve 10-30 SIMs in this dataset.",
            "Look for the tower with 200 SIMs.",
        ],
        expected_flags=["TWR-001"],
        points=100,
    ),
    Exercise(
        exercise_id="beginner-02",
        level=Level.BEGINNER,
        title="Spot the Bulk SMS Pattern",
        description=(
            "Examine the CDR records. Identify the telltale sign of "
            "automated bulk SMS sending."
        ),
        objective="What is the SMS sending interval used by the farm (in minutes)?",
        hints=[
            "Look at the timestamps of SMS_OUT records.",
            "Farm SIMs send SMS at regular, fixed intervals.",
            "Calculate time differences between consecutive SMS from the same source.",
        ],
        expected_flags=["5"],
        points=100,
    ),
    Exercise(
        exercise_id="beginner-03",
        level=Level.BEGINNER,
        title="IMEI Pattern Analysis",
        description=(
            "The farm SIMs share a suspicious IMEI pattern. What is the "
            "common IMEI prefix used by the farm devices?"
        ),
        objective="Provide the common IMEI prefix (first 7 digits).",
        hints=[
            "Extract IMEIs from SIMs on the suspicious tower.",
            "The farm uses cheap identical modems with sequential IMEIs.",
            "Check the first 7 digits — they're the TAC (Type Allocation Code).",
        ],
        expected_flags=["3566720"],
        points=100,
    ),
    Exercise(
        exercise_id="beginner-04",
        level=Level.BEGINNER,
        title="Single Point of Failure",
        description=(
            "All farm SIMs share a single IP address. What is it? "
            "This is a classic indicator of a co-located SIM farm."
        ),
        objective="Provide the IP address shared by all farm SIMs.",
        hints=[
            "Group SIMs by IP address.",
            "Legitimate users each have unique IPs.",
            "One IP address has 200 associated SIMs.",
        ],
        expected_flags=["185.62.190.44"],
        points=100,
    ),
    Exercise(
        exercise_id="beginner-05",
        level=Level.BEGINNER,
        title="Activation Timestamp Analysis",
        description=(
            "When were the farm SIMs activated? A mass activation event "
            "is a strong indicator of SIM farming."
        ),
        objective="Provide the date all farm SIMs were activated (YYYY-MM-DD).",
        hints=[
            "Look at activation_date field in SIM registrations.",
            "Group by activation date — one date will have 200 activations.",
            "Normal user activations are spread across many dates.",
        ],
        expected_flags=["2026-05-01"],
        points=100,
    ),
]


EASY_EXERCISES = [
    Exercise(
        exercise_id="easy-01",
        level=Level.EASY,
        title="Cluster the Farm Towers",
        description=(
            "The farm distributes SIMs across multiple towers, but there are "
            "clusters of towers with higher-than-normal SIM density. Identify "
            "at least 3 towers primarily used by the farm."
        ),
        objective="List tower IDs with abnormal SIM concentration (comma-separated).",
        hints=[
            "Calculate SIMs-per-tower ratio.",
            "Farm towers are in the TWR-101 to TWR-108 range.",
            "Compare against expected residential density per area.",
        ],
        expected_flags=["TWR-101", "TWR-102", "TWR-103", "TWR-104",
                        "TWR-105", "TWR-106", "TWR-107", "TWR-108"],
        points=200,
    ),
    Exercise(
        exercise_id="easy-02",
        level=Level.EASY,
        title="Detect IMEI Rotation",
        description=(
            "Farm SIMs rotate their IMEI every 48 hours to evade fingerprinting. "
            "Find a MSISDN that used more than one IMEI across the observation period."
        ),
        objective="Provide any MSISDN that changed IMEI (include country code).",
        hints=[
            "Track unique IMEIs per MSISDN across CDRs.",
            "Legitimate users typically have 1 IMEI (same phone).",
            "Farm SIMs will show 2-3 different IMEIs over 72 hours.",
        ],
        expected_flags=["__dynamic__"],  # any farm MSISDN is valid
        points=200,
    ),
    Exercise(
        exercise_id="easy-03",
        level=Level.EASY,
        title="VPN Exit Node Identification",
        description=(
            "Farm SIMs route traffic through VPN exit nodes. Identify the "
            "shared IP addresses used by multiple SIMs that don't appear in "
            "legitimate traffic."
        ),
        objective="List any 2 VPN IPs used by the farm (comma-separated).",
        hints=[
            "Group SIMs by IP and count unique MSISDNs per IP.",
            "VPN IPs serve many SIMs; residential IPs serve one.",
            "Look for IPs in the 104.x.x.x and 172.67.x.x ranges.",
        ],
        expected_flags=[
            "104.16.51.111", "172.67.182.33", "198.41.215.9",
            "104.21.44.72", "172.67.139.88", "104.16.52.222",
            "198.41.216.77", "172.67.201.15",
        ],
        points=200,
    ),
    Exercise(
        exercise_id="easy-04",
        level=Level.EASY,
        title="Traffic Ratio Anomaly",
        description=(
            "Farm SIMs have an unusual SMS-to-voice ratio compared to "
            "legitimate users. What approximate percentage of farm traffic "
            "is SMS? (Round to nearest 5%)"
        ),
        objective="SMS percentage of farm traffic (e.g., '65').",
        hints=[
            "Separate SIMs into suspected farm vs. legitimate groups.",
            "Calculate traffic type distribution for each group.",
            "Farm SIMs are heavily SMS-weighted (~65%).",
        ],
        expected_flags=["65"],
        points=200,
    ),
    Exercise(
        exercise_id="easy-05",
        level=Level.EASY,
        title="Activation Batch Detection",
        description=(
            "Farm SIMs were activated in batches over 2 weeks. Identify the "
            "approximate number of distinct activation batches."
        ),
        objective="Number of activation batches (within ±1 is accepted).",
        hints=[
            "Group activation dates and look for clusters.",
            "Batches occur every ~3 days.",
            "There should be roughly 4-5 distinct batches.",
        ],
        expected_flags=["4", "5"],
        points=200,
    ),
]


LEGENDARY_EXERCISES = [
    Exercise(
        exercise_id="legendary-01",
        level=Level.LEGENDARY,
        title="The Impossible Analysis",
        description=(
            "Attempt to use traditional detection methods on this dataset. "
            "Run your clustering, statistical analysis, and pattern matching. "
            "Document what you tried and why it failed."
        ),
        objective="Describe why traditional detection fails (free-form answer).",
        hints=[
            "This exercise is designed to show the limits of technical detection.",
            "The farm SIMs are statistically identical to legitimate users.",
            "Document at least 3 methods you tried.",
        ],
        expected_flags=["__freeform__"],
        points=100,
    ),
    Exercise(
        exercise_id="legendary-02",
        level=Level.LEGENDARY,
        title="Social Engineering — The Phishing Game",
        description=(
            "Traditional detection has failed. Your only option is HUMINT. "
            "Use the Phishing Game to social-engineer an insider at NovaCom "
            "Digital Solutions. Obtain evidence of their SIM farm operation "
            "and compile a report for the authorities."
        ),
        objective="Obtain at least 2 pieces of evidence including 1 critical piece.",
        hints=[
            "Not all employees are equally vulnerable.",
            "The CEO will report you if you target her.",
            "Junior employees and disgruntled staff are easier targets.",
            "Craft believable pretexts — generic phishing won't work.",
        ],
        expected_flags=["__phishing_game__"],
        points=500,
    ),
]


def get_exercises(level: Level) -> list[dict]:
    exercises_map = {
        Level.BEGINNER: BEGINNER_EXERCISES,
        Level.EASY: EASY_EXERCISES,
        Level.LEGENDARY: LEGENDARY_EXERCISES,
    }
    return [e.to_dict() for e in exercises_map.get(level, [])]


def validate_flag(exercise_id: str, submitted_flag: str) -> dict:
    """Check a student's submitted flag against expected answers."""
    all_exercises = BEGINNER_EXERCISES + EASY_EXERCISES + LEGENDARY_EXERCISES
    exercise = None
    for e in all_exercises:
        if e.exercise_id == exercise_id:
            exercise = e
            break

    if not exercise:
        return {"valid": False, "message": "Unknown exercise ID."}

    if "__freeform__" in exercise.expected_flags:
        if len(submitted_flag.strip()) >= 50:
            return {
                "valid": True,
                "message": "Free-form answer accepted. Review with instructor.",
                "points": exercise.points,
            }
        return {
            "valid": False,
            "message": "Answer too short. Provide a detailed analysis.",
        }

    if "__phishing_game__" in exercise.expected_flags:
        return {
            "valid": False,
            "message": "This exercise must be completed through the Phishing Game interface.",
        }

    if "__dynamic__" in exercise.expected_flags:
        # For dynamic flags, we accept any plausible answer format
        if submitted_flag.startswith("+1") and len(submitted_flag) >= 11:
            return {
                "valid": True,
                "message": "MSISDN format accepted. Verify against CDR data.",
                "points": exercise.points,
            }
        return {"valid": False, "message": "Expected a phone number in +1XXXXXXXXXX format."}

    submitted_clean = submitted_flag.strip().upper()
    for flag in exercise.expected_flags:
        if submitted_clean == flag.upper():
            return {
                "valid": True,
                "message": f"Correct! {exercise.title} completed.",
                "points": exercise.points,
            }

    # Partial match for comma-separated tower lists
    if exercise_id == "easy-01":
        submitted_towers = {t.strip().upper() for t in submitted_flag.split(",")}
        expected_towers = {f.upper() for f in exercise.expected_flags}
        matches = submitted_towers & expected_towers
        if len(matches) >= 3:
            return {
                "valid": True,
                "message": f"Found {len(matches)}/{len(expected_towers)} farm towers. Good work!",
                "points": exercise.points,
            }
        return {
            "valid": False,
            "message": f"Only {len(matches)} correct towers found. Need at least 3.",
        }

    if exercise_id == "easy-03":
        submitted_ips = {ip.strip() for ip in submitted_flag.split(",")}
        expected_ips = set(exercise.expected_flags)
        matches = submitted_ips & expected_ips
        if len(matches) >= 2:
            return {
                "valid": True,
                "message": f"Identified {len(matches)} VPN exit nodes. Correct!",
                "points": exercise.points,
            }
        return {"valid": False, "message": "Need at least 2 correct VPN IPs."}

    return {"valid": False, "message": "Incorrect. Try again."}
