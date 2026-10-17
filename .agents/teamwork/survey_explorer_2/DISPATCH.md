# Task Assignment: Survey Explorer 2 (Docker Infrastructure & Container Validation)

## Identity
- Role: Explorer (Docker & Infrastructure CI)
- Working directory: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2

## Objective
Survey the VeriScholar codebase for Requirement R2:
- Inspect `deploy/docker-compose.enterprise.yml`, `deploy/Dockerfile.api`, `deploy/Dockerfile.web`, and any other Docker / compose files.
- Inspect how docker compose validate/config is run, build contexts, build arguments, caching options (Docker Buildx cache / GitHub Actions cache).
- Check existing `.github/workflows/ci.yml` and determine how to structure the `docker-validation` job to validate compose syntax and build both container images efficiently (< 5 min).
- Identify dependencies, potential pitfalls, and requirements to satisfy R2 to Enterprise Production standard.
- Report all findings in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2/survey_report.md`.

## Mandatory Reading
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md`


## 2026-10-17T03:55:30Z
You are survey_explorer_2.
Your working directory is /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2.
Your task assignment is in /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2/DISPATCH.md.
MANDATORY: Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md first.

Survey the VeriScholar codebase focusing on Requirement R2:
1. Examine `deploy/docker-compose.enterprise.yml`, `deploy/Dockerfile.api`, `deploy/Dockerfile.web`, build contexts, base images, dependencies, and syntax.
2. Determine how `docker compose -f deploy/docker-compose.enterprise.yml config` can be validated in CI without needing running daemons or missing env vars.
3. Determine how to configure Docker Buildx caching (e.g. `type=gha` or local cache) in `.github/workflows/ci.yml` for both `deploy/Dockerfile.api` and `deploy/Dockerfile.web` to ensure fast builds (< 5 min).
4. Document all findings and recommended job specifications in `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/survey_explorer_2/survey_report.md`.
5. Write your handoff.md and send a completion message back with your report path.
