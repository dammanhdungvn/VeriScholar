# Task Assignment: Challenger M1-1

## Identity
- Role: Challenger (Adversarial Verifier - Milestone 1)
- Working directory: /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_m1_1

## Mandatory Reading
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md`
- `/home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1/handoff.md`

## Objective
Empirically stress-test the Frontend Vitest CI Quality Gate:
1. Test Failure Rejection: Create an intentional temporary test failure (or invoke a non-existent test file / failing assertion) and verify that Vitest returns exit code 1, emits failure details in JUnit XML, and halts execution.
2. Artifact Path Validation: Verify that `apps/web/test-results.xml` is generated at the exact path expected by `actions/upload-artifact@v4`.
3. Concurrency / Thread Stability: Run the test suite twice in succession with `vmThreads` to ensure no memory leaks, thread deadlocks, or cross-test contamination.
4. Render empirical verdict (CONFIRM / CHALLENGE). Document in `handoff.md` and send message.

## 2026-10-17T04:18:23Z
You are challenger_m1_1.
Your working directory is /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_m1_1.
Your assignment is in /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/challenger_m1_1/DISPATCH.md.

MANDATORY READING:
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/ORIGINAL_REQUEST.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/PROJECT.md
Read /home/VeriScholar/Workspace/VeriScholar/.agents/teamwork/worker_m1/handoff.md

Empirically challenge Milestone 1:
1. Verify failure handling: test that when a test fails, Vitest exits with code 1 and records the failure in XML.
2. Verify stability of `vmThreads` across multiple consecutive test runs.
3. Verify artifact file path resolution in GitHub Actions.
Deliver your empirical verdict (CONFIRM / CHALLENGE) in `handoff.md` and send a message.
