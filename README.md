# SimFarm Security Lab

A hands-on cybersecurity training platform for detecting SIM farm operations.

Built for cybersecurity students to learn how SIM farms operate, how to detect them
using telecom forensics, and why closed systems require human intelligence (HUMINT).

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

Open `http://localhost:8000` in your browser.

### Local Development

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Levels

### Beginner — "The Obvious Farm"
Blatant SIM farm with sequential IMEIs, single tower, bulk SMS at fixed intervals.
Detection: Simple pattern matching.

### Easy — "The Hidden Network"
VPN tunneling, IMEI rotation, distributed towers, staggered activation.
Detection: Statistical clustering, temporal correlation, cross-referencing.

### Legendary — "The Ghost Farm"
Persona-driven behavior indistinguishable from real users. 99.9% undetectable.
Detection: Social engineering via the **Phishing Game** — students must
phish an insider at the front company to obtain evidence.

## Requirements

- Docker, or Python 3.11+
- `CPU 2` | `RAM 2G` | `HDD 1G`

## Disclaimer

This lab is provided strictly for **educational and training use**.
Never apply these techniques against real individuals or systems
without explicit authorization.

## License

MIT
