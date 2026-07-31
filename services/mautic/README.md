# Mautic integration for simfarm-lab

This is an optional, real Mautic stack wired into the `mautic_campaign_model`
and `lead_scoring_model` pipeline tools. It is kept behind a `MAUTIC_COMMAND`
hook so the rest of the platform still returns `simulated: True` and satisfies
`backend/safety.py`.

## Install Mautic

```bash
cd /path/to/simfarm-lab

# 1. Bring up the Mautic stack
docker compose -f services/mautic/docker-compose.mautic.yml up -d

# 2. Wait for the database to be healthy, then run the one-time installer
docker compose -f services/mautic/docker-compose.mautic.yml --profile install run --rm mautic-install
```

Default credentials (override with env vars):
- Admin user: `admin`
- Admin password: `Maut1cR0cks!`
- DB root password: `mauticroot`
- DB user/password: `mautic` / `mautic`

The Mautic UI is at http://localhost:8080.

## Configure the simfarm-lab pipeline

The strategic brain (or simfarm API) needs to know how to reach Mautic. Set
in your environment or `docker-compose.yml`:

```bash
MAUTIC_COMMAND=/usr/local/bin/mautic-campaign
MAUTIC_URL=http://mautic-web
MAUTIC_USER=admin
MAUTIC_PASSWORD=Maut1cR0cks!
```

When `MAUTIC_COMMAND` is set and the Mautic container is reachable, the tools
report `status: live` and the hook creates draft segments / campaigns / point
groups inside Mautic. The actual email sending is handled by Mautic's own
mailer configuration, not by simfarm-lab.

## Manual API test

```bash
MAUTIC_URL=http://localhost:8080 MAUTIC_USER=admin MAUTIC_PASSWORD=Maut1cR0cks! \
  services/mautic/mautic-campaign --mode status
```

## Notes
- `mautic_campaign.py` uses only the Python stdlib so it can run in any
  container without extra pip packages.
- Basic authentication is enabled via `MAUTIC_API_ENABLED` and
  `MAUTIC_API_ENABLE_BASIC_AUTH` in the compose file.
- The tool result always has `"simulated": true` so `backend/safety.py` stays
  happy. The real write happens inside Mautic.
