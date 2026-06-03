"""Detection engine — tools students can use to analyze data."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime


def analyze_tower_distribution(sim_cards: list[dict]) -> dict:
    """Count SIMs per cell tower."""
    tower_counts = Counter(s["cell_tower_id"] for s in sim_cards)
    return {
        "tower_distribution": dict(tower_counts.most_common()),
        "total_sims": len(sim_cards),
        "unique_towers": len(tower_counts),
        "avg_sims_per_tower": round(len(sim_cards) / max(len(tower_counts), 1), 1),
    }


def analyze_imei_patterns(sim_cards: list[dict]) -> dict:
    """Analyze IMEI distribution for sequential/duplicate patterns."""
    imeis = [s["imei"] for s in sim_cards]
    prefixes = Counter(imei[:7] for imei in imeis)
    models = Counter(s["device_model"] for s in sim_cards)
    return {
        "imei_prefix_distribution": dict(prefixes.most_common(10)),
        "device_model_distribution": dict(models.most_common(10)),
        "unique_imeis": len(set(imeis)),
        "total_sims": len(sim_cards),
        "duplicate_imeis": len(imeis) - len(set(imeis)),
    }


def analyze_activation_dates(sim_cards: list[dict]) -> dict:
    """Analyze SIM activation date clusters."""
    date_counts = Counter(s["activation_date"] for s in sim_cards)
    sorted_dates = sorted(date_counts.items())
    return {
        "activation_timeline": dict(sorted_dates),
        "peak_date": date_counts.most_common(1)[0] if date_counts else None,
        "date_spread_days": _date_spread(sorted_dates),
        "total_sims": len(sim_cards),
    }


def _date_spread(sorted_dates: list) -> int:
    if len(sorted_dates) < 2:
        return 0
    first = datetime.strptime(sorted_dates[0][0], "%Y-%m-%d")
    last = datetime.strptime(sorted_dates[-1][0], "%Y-%m-%d")
    return (last - first).days


def analyze_ip_distribution(sim_cards: list[dict]) -> dict:
    """Analyze IP address sharing patterns."""
    ip_counts = Counter(s["ip_address"] for s in sim_cards)
    shared_ips = {ip: count for ip, count in ip_counts.items() if count > 1}
    return {
        "ip_distribution": dict(ip_counts.most_common(20)),
        "shared_ips": shared_ips,
        "unique_ips": len(ip_counts),
        "sims_on_shared_ips": sum(shared_ips.values()),
    }


def analyze_traffic_patterns(cdrs: list[dict]) -> dict:
    """Analyze traffic type distribution per MSISDN."""
    per_msisdn: dict[str, Counter] = defaultdict(Counter)
    for cdr in cdrs:
        per_msisdn[cdr["source_msisdn"]][cdr["traffic_type"]] += 1

    sms_heavy = []
    balanced = []
    for msisdn, counts in per_msisdn.items():
        total = sum(counts.values())
        sms_count = counts.get("sms_out", 0) + counts.get("sms_in", 0)
        sms_ratio = sms_count / max(total, 1)
        if sms_ratio > 0.8:
            sms_heavy.append(msisdn)
        elif 0.2 < sms_ratio < 0.6:
            balanced.append(msisdn)

    return {
        "sms_heavy_sims": len(sms_heavy),
        "balanced_sims": len(balanced),
        "total_analyzed": len(per_msisdn),
        "sample_sms_heavy": sms_heavy[:5],
    }


def analyze_temporal_patterns(cdrs: list[dict]) -> dict:
    """Analyze timing patterns — look for regular intervals."""
    per_msisdn: dict[str, list[str]] = defaultdict(list)
    for cdr in cdrs:
        if cdr["traffic_type"] == "sms_out":
            per_msisdn[cdr["source_msisdn"]].append(cdr["timestamp"])

    regular_senders = []
    for msisdn, timestamps in per_msisdn.items():
        if len(timestamps) < 10:
            continue
        timestamps.sort()
        intervals = []
        for i in range(1, min(len(timestamps), 20)):
            t1 = datetime.fromisoformat(timestamps[i - 1])
            t2 = datetime.fromisoformat(timestamps[i])
            intervals.append((t2 - t1).total_seconds())

        if intervals:
            avg = sum(intervals) / len(intervals)
            variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
            std_dev = variance ** 0.5
            cv = std_dev / max(avg, 1)  # coefficient of variation
            if cv < 0.3:  # very regular
                regular_senders.append({
                    "msisdn": msisdn,
                    "avg_interval_seconds": round(avg, 1),
                    "coefficient_of_variation": round(cv, 3),
                })

    return {
        "regular_senders": len(regular_senders),
        "total_analyzed": len(per_msisdn),
        "sample_regular": regular_senders[:5],
    }


def analyze_imei_changes(cdrs: list[dict]) -> dict:
    """Track IMEI changes per MSISDN across CDRs."""
    per_msisdn: dict[str, set[str]] = defaultdict(set)
    for cdr in cdrs:
        per_msisdn[cdr["source_msisdn"]].add(cdr["imei"])

    changers = {
        msisdn: list(imeis)
        for msisdn, imeis in per_msisdn.items()
        if len(imeis) > 1
    }

    return {
        "sims_with_imei_changes": len(changers),
        "total_analyzed": len(per_msisdn),
        "sample_changers": dict(list(changers.items())[:5]),
    }


def analyze_contact_graph(cdrs: list[dict]) -> dict:
    """Relationship forensics: contact reciprocity and clustering per subscriber.

    Genuine subscribers have reciprocal, clustered ego-networks (people they
    talk to also talk back, and their contacts know each other). Verification /
    OTP farm lines emit to many one-off numbers that never reply and do not know
    each other, producing a low-reciprocity, low-clustering, star-shaped
    ego-network. This is the most durable behavioral signal against a farm whose
    per-line statistics are otherwise indistinguishable from real users.

    For each subscriber with enough relationship data we compute:

    * ``reciprocity`` — fraction of the parties it contacted that also contacted
      it back.
    * ``clustering`` — fraction of its contacts that are connected to each other.

    A line is flagged as *suspicious* when both scores are near zero.
    """
    # Directed edges X -> Y from human (SMS/voice) traffic only.
    out_edges: dict[str, set[str]] = defaultdict(set)
    in_edges: dict[str, set[str]] = defaultdict(set)
    neighbors: dict[str, set[str]] = defaultdict(set)

    voice_sms = {"sms_out", "sms_in", "voice_out", "voice_in"}
    for cdr in cdrs:
        if cdr.get("traffic_type") not in voice_sms:
            continue
        src = cdr.get("source_msisdn") or ""
        dst = cdr.get("destination_msisdn") or ""
        if not src or not dst:
            continue
        out_edges[src].add(dst)
        in_edges[dst].add(src)
        neighbors[src].add(dst)
        neighbors[dst].add(src)

    # Minimum distinct contacts required to judge a line (low-activity lines are
    # "inconclusive" rather than flagged — you cannot judge a relationship graph
    # from a handful of events).
    min_contacts = 5

    scored: list[dict] = []
    suspicious: list[dict] = []
    for msisdn, outs in out_edges.items():
        contacted = set(outs)
        if len(contacted) < min_contacts:
            continue
        replied_back = {c for c in contacted if msisdn in out_edges.get(c, set())}
        reciprocity = len(replied_back) / max(len(contacted), 1)

        # Local clustering: of all pairs among this line's neighbors, how many
        # are directly connected?
        neigh = list(neighbors[msisdn])
        links = 0
        pairs = 0
        for a_idx in range(len(neigh)):
            for b_idx in range(a_idx + 1, len(neigh)):
                pairs += 1
                a, b = neigh[a_idx], neigh[b_idx]
                if b in neighbors.get(a, set()) or a in neighbors.get(b, set()):
                    links += 1
        clustering = links / pairs if pairs else 0.0

        entry = {
            "msisdn": msisdn,
            "contacts": len(contacted),
            "reciprocity": round(reciprocity, 3),
            "clustering": round(clustering, 3),
        }
        scored.append(entry)
        if reciprocity < 0.15 and clustering < 0.10:
            suspicious.append(entry)

    suspicious.sort(key=lambda e: (e["reciprocity"], e["clustering"]))
    avg_recip = round(sum(e["reciprocity"] for e in scored) / max(len(scored), 1), 3)
    return {
        "subscribers_analyzed": len(scored),
        "low_reciprocity_count": len(suspicious),
        "avg_reciprocity": avg_recip,
        "threshold": {"reciprocity": 0.15, "clustering": 0.10, "min_contacts": min_contacts},
        "sample_suspicious": suspicious[:10],
        "note": (
            "Lines with near-zero reciprocity AND clustering form a star-shaped "
            "ego-network — a strong lead for a verification/OTP farm. This is a "
            "lead, not proof: corroborate via HUMINT before referral."
        ),
    }


ANALYSIS_TOOLS = {
    "tower_distribution": analyze_tower_distribution,
    "imei_patterns": analyze_imei_patterns,
    "activation_dates": analyze_activation_dates,
    "ip_distribution": analyze_ip_distribution,
    "traffic_patterns": analyze_traffic_patterns,
    "temporal_patterns": analyze_temporal_patterns,
    "imei_changes": analyze_imei_changes,
    "contact_graph": analyze_contact_graph,
}
