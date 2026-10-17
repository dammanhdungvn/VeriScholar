# Task Assignment: Survey Spec Miner 3 (CD Pipeline, Zero-Downtime, Rollback & Architecture Audit)

## Identity
- Role: Spec Miner / Explorer (CD Pipeline & System Audit)
- Working directory: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_miner_3

## Objective
Survey the VeriScholar codebase for Requirements R3 and R4:
- Inspect any existing CD workflows (e.g. `.github/workflows/cd.yml`), deployment scripts (e.g. `scripts/deploy_web.sh`, systemd service configs, nginx configs, etc.).
- Inspect the database migration mechanism (e.g. `init_db.py`, idempotent DDL `ADD COLUMN IF NOT EXISTS`, Alembic if any).
- Inspect the live system architecture, host setup, duckdns endpoint (`https://verischolar.duckdns.org/health`), service management (e.g. systemd, docker, or process manager), and rollback mechanics (git checkout prior commit, service restart, verification).
- Survey requirements for R4: architecture audit, simulation of failure scenarios, measuring pipeline execution time, certification criteria.
- Report all findings in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_miner_3/survey_report.md`.

## Mandatory Reading
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md`


## 2026-10-17T03:55:30Z
You are survey_miner_3.
Your working directory is /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_miner_3.
Your task assignment is in /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_miner_3/DISPATCH.md.
MANDATORY: Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md first.

Survey the VeriScholar codebase focusing on Requirements R3 & R4:
1. Inspect deployment scripts (e.g. `scripts/deploy_web.sh`, any cd workflows `.github/workflows/cd.yml`, systemd services, nginx config).
2. Inspect database migration logic (`init_db.py`, schema definitions, DDL idempotence e.g. `ADD COLUMN IF NOT EXISTS`).
3. Inspect how the live production service is hosted at `https://verischolar.duckdns.org`, how the backend API and frontend Nginx are deployed and restarted, and how health checks at `https://verischolar.duckdns.org/health` work.
4. Formulate the concrete design for the CD pipeline with Zero-Downtime DB migration and automatic 30s rollback if health check fails.
5. Survey requirements for R4 architecture audit and Quality Gate certification.
6. Document all findings in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_miner_3/survey_report.md`.
7. Write your handoff.md and send a completion message back with your report path.
