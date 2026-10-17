# Progress — Worker M2 (Requirement R2: Docker & Container CI Gate)

Last visited: 2026-10-17T04:32:45Z

## Status
- [x] Read referenced documents (ORIGINAL_REQUEST.md, PROJECT.md, survey_explorer_2/survey_report.md, survey_explorer_2/handoff.md, DISPATCH.md)
- [x] Reproduced failure: `docker build -f deploy/Dockerfile.api .` failed at Step 7/7 with flat-layout discovery error
- [x] Verified offline docker-compose config passes (defaults and .env.enterprise)
- [ ] Task 1: Update `pyproject.toml` with `[tool.setuptools] packages = []`
- [ ] Task 2: Create root `.dockerignore` to exclude node_modules, .venv, .git, etc.
- [ ] Task 3: Update `.github/workflows/ci.yml` (detect-changes filters + docker-validation job with dual compose config and Buildx GHA cache)
- [ ] Task 4: Verify `docker build -f deploy/Dockerfile.api .` succeeds (exit code 0)
- [ ] Task 5: Verify `docker build -f deploy/Dockerfile.web .` succeeds (exit code 0, context < 1MB)
- [ ] Task 6: Validate YAML syntax of `.github/workflows/ci.yml`
- [ ] Task 7: Run ruff check and full test suite to guarantee zero regression
- [ ] Task 8: Write handoff.md and report to caller
