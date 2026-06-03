# SimFarm Security Lab — Architecture

## Overview
A Docker-based cybersecurity training platform for detecting SIM farming operations.
Three progressive difficulty levels teach students how SIM farms operate, how to detect them,
and why closed systems require human intelligence (HUMINT) to uncover.

## Tech Stack
- **Frontend**: Vanilla HTML/CSS/JS (lightweight, no build step)
- **Backend**: Python 3.11 + FastAPI
- **Database**: SQLite (portable, zero-config)
- **Deployment**: Docker + Docker Compose

## Levels

### Beginner — "The Obvious Farm"
- 200 SIM cards registered on the **same cell tower**
- Bulk SMS every 5 minutes, no voice calls
- Sequential IMEI pattern (easy to spot)
- All SIMs activated the same day
- Single originating IP address
- **Detection**: Simple log grep, pattern matching on CDRs

### Easy — "The Hidden Network"
- SIMs distributed across **15 cell towers**
- Staggered activation over 2 weeks
- Mixed traffic (voice + SMS + data)
- IMEI rotation every 48 hours, multiple IPs with VPN
- **Detection**: Statistical clustering, temporal correlation, SIM ↔ IMEI mapping anomalies

### Legendary — "The Ghost Farm"
- Each SIM mimics a real human user (calls, browsing, apps)
- Physically distributed across a city (simulated GPS)
- Unique device fingerprints, human-like timing jitter
- **No shared infrastructure visible externally**
- Anti-forensic measures active
- **Detection**: Impossible via traffic alone → **HTML Phishing Game**

## Phishing Game (Legendary Detection)
Students must social-engineer a simulated insider:
1. **Recon phase**: Browse a fake company directory + social media profiles
2. **Craft phase**: Write phishing emails / messages targeting employees
3. **Interact phase**: NPCs respond based on trust level and email quality
4. **Evidence phase**: Successful phish reveals internal documents proving the SIM farm
5. **Report phase**: Compile evidence and submit to "authorities"

Scoring: stealth × effectiveness × evidence quality

## Component Map

```
┌────────────────────────────────────────────┐
│                Web Portal                  │
│  Dashboard │ Exercises │ Phishing Game     │
└────────────┬───────────┬───────────────────┘
             │  REST API │
┌────────────▼───────────▼───────────────────┐
│            FastAPI Backend                  │
│  Simulator │ Detection Engine │ Game Logic  │
└────────────┬───────────┬───────────────────┘
             │           │
        ┌────▼───┐  ┌────▼────┐
        │ SQLite │  │  Logs   │
        └────────┘  └─────────┘
```
