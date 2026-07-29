"""TIER 4 — isolated SIM-farm / GSM-gateway simulator service.

A standalone, internal-only FastAPI service that models the physical scaffolding
of a SIM farm (GSM modems, SMSgate/Gammu gateway, number provisioning, Celery
campaign orchestration) for authorized detection-research and training.

It is a SIMULATOR: every response is ``simulated: true`` and nothing here ever
touches real hardware, real SIMs, real modems, real carriers, real phone
numbers, real OTPs, or real message delivery. There is no code path that
performs real telecom activity — the "simulated" flag cannot be turned off.
"""
