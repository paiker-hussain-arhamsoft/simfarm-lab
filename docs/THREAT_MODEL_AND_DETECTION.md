# SIM-Farm Threat Model & Detection Reference (Instructor / Blue-Team)

> **Audience & purpose.** This document is written for instructors and analysts using
> SimFarm Security Lab to teach **detection, forensics, and investigation** of SIM-farm
> telecom fraud. It is deliberately a *defender-facing* reference. For every technique it
> describes **what the technique is**, **the threat it poses**, **the legitimate uses of the
> same underlying capability** (dual-use), and — the part that matters for this lab — **the
> indicators a defender can use to detect it** and the **countermeasures** that reduce it.
>
> **What this document is not.** It is not an operations manual. It intentionally does **not**
> contain step-by-step procurement instructions, identity/verification-bypass procedures, or
> an evasion-tuning recipe. Those would be an operational playbook for committing fraud, and
> they are out of scope regardless of how the lab is used. The lab's playground module
> (`backend/simulator/playground.py`) simulates an attacker's *choices* so students can learn
> which choices are **detectable**; this document is the defender's mirror of that.
>
> This format follows the convention used by public defensive knowledge bases such as
> MITRE ATT&CK and GSMA fraud-intelligence material: name the technique, describe it,
> enumerate detection and mitigation. Naming a technique and how to *catch* it is defensive
> knowledge; describing how to *perform and conceal* it is not, and is omitted here.

---

## 1. What a SIM farm is, and why it matters

A **SIM farm** is an array of mobile subscriber identities (SIMs) operated together,
typically programmatically, to abuse the trust the telecom and digital ecosystem places in
"a phone number = a real person." The same hardware/software that powers a legitimate bulk
A2P (application-to-person) messaging business is, when pointed at fraud, used for:

| Abuse | What the attacker monetizes |
|---|---|
| **OTP / verification harvesting** | Mass-create or take over accounts that gate on SMS one-time passwords |
| **Bulk SMS spam / smishing** | Deliver phishing and scam messages at carrier-trusted rates |
| **Call-termination (interconnect bypass) fraud** | Terminate international VoIP onto local SIMs to dodge interconnect fees |
| **Money-mule / mobile-money fraud** | Open large numbers of wallet accounts (e.g. JazzCash/Easypaisa) |
| **Influence operations** | Stand up large numbers of "authentic-looking" social accounts |

**Why it is hard.** Detection is an asymmetric game. Beginner operators leave blatant
artifacts; sophisticated operators deliberately make each line look like an ordinary human
subscriber. The lab's three levels model that progression so students learn that detection
moves from **simple aggregate statistics** → **correlation/behavioral analysis** →
**graph/relationship forensics + human intelligence** as the adversary improves.

---

## 2. Data artifacts an investigator works with

| Artifact | Description | Primary signal it carries |
|---|---|---|
| **CDR** (Call Detail Record) | One row per SMS/voice/data event | Timing, volume, traffic mix, contact relationships |
| **Subscriber / SIM registration** | ICCID, IMSI, MSISDN, IMEI, activation, registered identity | Identity reuse, batch activation, device reuse |
| **Cell-tower attach logs** | Which tower/sector served a SIM and when | Co-location, implausible mobility |
| **Network / IP logs** | Source IP, destination, ports | Shared egress, hosting/VPN ranges vs residential |
| **Provisioning / funding records** | Top-ups, payment instruments, retailer of sale | Common funding source, common point of sale |
| **HUMINT / OSINT** | Insider testimony, public footprint of the front company | Confirmation that statistical leads point at a real operation |

The lab exposes the first four directly to students; provisioning/funding and HUMINT appear
at the Legendary level, mirroring real investigations where pure traffic forensics must be
corroborated by financial-intelligence and human sources.

---

## 3. Technique catalog (defender view)

Each entry: **Definition → Threat → Legitimate / dual-use → Detection indicators →
Countermeasures.** Techniques are grouped by the kill-chain stage they belong to. These are
the technique *classes* present in the lab; the entries describe them at a conceptual level
and focus on detection.

### 3.1 Identity acquisition & registration abuse

**Definition.** Obtaining many subscriber identities while defeating the "one identity →
limited SIMs" control. In a strict-KYC ecosystem (e.g. Pakistan: CNIC + biometric at point
of sale, per-CNIC SIM caps enforced by PTA/NADRA) this spans a spectrum from *legitimate
multi-SIM ownership*, through *recruiting real people to register on their behalf*, to
outright *identity fraud* (forged/stolen identity data, complicit retail agents).

**Threat.** Breaks attribution. If the registered identity is fake, stolen, or a paid proxy,
the line cannot be traced back to the operator, defeating downstream accountability.

**Legitimate / dual-use.** Enterprises legitimately hold thousands of SIMs (fleet telematics,
IoT, POS terminals) under corporate accounts; families share registrations; MVNO resellers
provision in bulk. The capability "register many SIMs" is normal — intent and concealment are
what make it abuse.

**Detection indicators.**
- One registered identity (or a small set) associated with far more lines than the
  regulatory cap, especially across multiple carriers.
- **Batch activation**: many activations clustered in narrow time windows (a strong beginner/
  easy signal; sophisticated actors spread activations over months to defeat it).
- Corporate/enterprise accounts whose *usage* (outbound OTP/SMS bursts) does not match the
  stated business purpose (IoT telemetry, etc.).
- Registered-identity demographics inconsistent with usage (e.g. lines registered to elderly
  rural CNICs generating high-volume urban OTP traffic).
- Cross-reference registration biometrics against the national identity database for reuse or
  liveness failures (regulator-side control).

**Countermeasures.** Enforce and audit per-identity caps across carriers; biometric liveness
at point of sale; KYC re-verification on anomalous usage; agent/retailer accountability and
audit of activations per outlet; data-sharing between carriers and the regulator.

---

### 3.2 Device / IMEI manipulation

**Definition.** Reusing, cloning, or rotating device identifiers (IMEI) so that the
device↔SIM relationship cannot be fingerprinted, frustrating systems such as DIRBS that pair
IMEIs to registered devices.

**Threat.** Defeats device-based blocking and link analysis; lets cheap multi-port hardware
masquerade as many distinct handsets.

**Legitimate / dual-use.** Device testing labs, refurbishers, and repair shops legitimately
re-flash or test many IMEIs; carriers re-provision devices. The act of changing an identifier
is not inherently malicious.

**Detection indicators.**
- **Shared / sequential IMEI prefixes (TAC)**: many lines on cheap identical modem hardware
  share a Type Allocation Code — a beginner-level giveaway.
- **One MSISDN seen with multiple IMEIs** over a short window (rotation) — an easy/medium
  signal: ordinary subscribers keep one handset for long periods.
- IMEIs absent from or inconsistent with the device-registration whitelist.
- Implausible device model vs. traffic profile (a "premium handset" that only ever emits
  short OTP SMS and never browses).

**Countermeasures.** IMEI whitelisting/registration (DIRBS-style), pairing-history analytics,
flagging IMEI churn per MSISDN, blocking known multi-SIM gateway TACs.

---

### 3.3 Infrastructure & egress concentration

**Definition.** The physical/network plumbing — GSM modem pools, SIM banks, SIM/VoIP boxes,
phone farms — and the data egress (shared connection, VPN/proxy) behind it.

**Threat.** Concentrated infrastructure is efficient for the operator but creates
co-location signal; the trade-off operators manage is *throughput vs. detectability*.

**Legitimate / dual-use.** Legitimate A2P aggregators, SMS gateways, and contact centers run
the same modem pools and SMPP infrastructure; VPNs are ubiquitous privacy tools.

**Detection indicators.**
- **Many SIMs egressing from one IP** or a small hosting/VPN range, versus one residential IP
  per genuine subscriber (a beginner/easy signal).
- Many SIMs persistently attaching to **one tower/sector** beyond plausible residential
  density (co-location).
- Traffic sourced from data-center/VPN ASNs rather than residential ISPs.
- SMPP/gateway-style delivery patterns (high, sustained, uniform throughput).

**Countermeasures.** IP/ASN reputation and density thresholds, per-cell subscriber-density
baselining, correlation of egress IP to subscriber count, A2P traffic registration so
legitimate bulk senders are known and the rest is suspect.

---

### 3.4 Behavioral & temporal evasion (the Legendary problem)

**Definition.** Making each line *behave* like a human: human-plausible active hours,
**Poisson-distributed** (not fixed-interval) timing, persona-appropriate traffic mix,
geographic plausibility, unique device/IP per line. This is the core of a "ghost" farm.

**Threat.** Defeats every *aggregate-statistics* detector. Tower distribution, IMEI prefixes,
IP sharing, traffic-ratio, and fixed-interval timing all come back clean. This is exactly the
trap the Legendary level sets — and the lesson is that **aggregate statistics are necessary
but not sufficient.**

**Legitimate / dual-use.** "Behaving like a normal user" is, definitionally,
indistinguishable from being a normal user at the single-line level — which is why
single-line analysis fails and the investigation must move up to *relationships* and
*corroboration*.

**Detection indicators (where the ghost still leaks).**
- **Contact-graph reciprocity.** Genuine subscribers have *reciprocal, clustered* social
  graphs: people they text also text them, and their contacts know each other (triangles).
  OTP/verification farm lines emit to many one-off external numbers that **never reply** and
  **don't know each other** — a low-reciprocity, low-clustering, star-shaped ego-network.
  This is the single most durable behavioral signal and is hard to fake at scale. *(The lab
  surfaces this via the new `contact_graph` analysis tool and the Legendary graph exercise.)*
- **Inter-line activity correlation.** Lines under one controller share scheduling: their
  active/dormant windows correlate across the fleet more than independent humans' would, even
  with per-line jitter. Cross-correlate per-MSISDN activity time series.
- **Mobility plausibility.** Randomly assigned "home"/"work" towers can yield physically
  impossible commutes or improbable numbers of lines sharing the exact same home+work pair.
- **Funding/provisioning correlation.** "Human" lines whose top-ups trace to a common payment
  instrument, retailer, or funding cadence.
- **Reciprocity of value.** Lines that only ever *receive* verification SMS from service short
  codes and never engage in genuine two-way human conversation.

**Countermeasures.** Graph-analytics on the social/contact network; entity-resolution across
funding and provisioning; fusion of weak signals (no single one is conclusive); and, when
statistical leads converge on a suspected front, **corroboration via financial intelligence
and HUMINT/OSINT** rather than traffic data alone.

---

### 3.5 Why the Legendary level needs HUMINT

At the top end, traffic forensics produces **leads, not proof**. Real cases against
sophisticated operations are closed by combining: (a) subtle behavioral/graph leads, (b)
financial-intelligence (mule accounts, funding), and (c) human sources / undercover work that
tie the lines to a physical operation and named operators. The lab models (c) through the
phishing/HUMINT game — and the pedagogical point is *escalation discipline*: do not jump to
intrusive human-source methods until cheaper forensic avenues are exhausted, and operate only
within legal authority. (See §5.)

---

## 4. Detection workflow taught by the lab

1. **Triage with aggregate statistics** (tower density, IMEI prefixes, IP sharing, activation
   batches, traffic ratios, fixed-interval timing). Catches Beginner; dents Easy.
2. **Correlation & behavioral analysis** (IMEI rotation per MSISDN, VPN-range clustering,
   staggered-batch detection). Required for Easy.
3. **Relationship / graph forensics** (contact-graph reciprocity & clustering, inter-line
   activity correlation, mobility plausibility). The only *technical* path that dents
   Legendary.
4. **Corroboration** (financial intelligence + HUMINT/OSINT). Converts Legendary leads into a
   referable case.

The scoring engine reports **precision / recall / F1** against ground truth so students learn
that over-flagging (false positives) is itself a failure mode — a real investigator who flags
every line is as useless as one who flags none.

---

## 5. Ethics, legality, and supervised use

- **Dual-use is real and should be taught explicitly.** Every capability here (bulk
  messaging, multi-SIM ownership, IMEI re-flashing, VPNs, automation) has mainstream
  legitimate uses. The differentiators are **intent, consent, authorization, and
  concealment**. Teach students to articulate that distinction, not just the mechanics.
- **The "stated justification" vs. reality framing.** Operators often wrap an operation in a
  legitimate-sounding cover ("cloud communications", "bulk verification SaaS"). Instructors
  should use this to teach students to look past the stated purpose to the *observable
  behavior* — which is the entire premise of detection.
- **Authority and proportionality.** Detection, investigation, and especially human-source
  methods must operate within legal authority (lawful intercept, warrants, regulator powers)
  and proportionality. The lab's HUMINT game is a *teaching abstraction* for understanding why
  HUMINT is needed and how it is corroborated — not a license to phish real people.
- **Containment.** This lab generates only synthetic data and simulated scenarios. It is
  intended for closed, supervised instructional environments. It must not be connected to real
  telecom infrastructure, real identities, or live targets.

---

## 6. Mapping to the lab levels

| Level | Adversary sophistication | Technique classes present | Detection path |
|---|---|---|---|
| **Beginner — "The Obvious Farm"** | None | Co-location, shared IP, sequential IMEIs, fixed-interval bulk SMS, mass activation | Aggregate statistics |
| **Easy — "The Hidden Network"** | Moderate evasion | Distributed towers, IMEI rotation, VPN egress, staggered batches, partial diversity | Correlation & behavioral analysis |
| **Legendary — "The Ghost Farm"** | Near-undetectable per-line | Behavioral/temporal mimicry, unique device+IP per line, persona modeling | Graph forensics (leads) **+** HUMINT/financial corroboration (proof) |

---

*This reference is part of SimFarm Security Lab and is intended solely for supervised
cybersecurity instruction in catching and investigating telecom fraud.*
