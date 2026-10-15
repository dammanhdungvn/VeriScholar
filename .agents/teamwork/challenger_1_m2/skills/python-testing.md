# Python Testing Patterns Summary
Source: /home/dammanhdungvn/Downloads/Workspace/VeriScholar/.agents/skills/python-testing/SKILL.md

Core Methodology:
- Write failing tests (RED) then minimal fixes (GREEN).
- Target: 80%+ coverage.
- Parametrized tests with `@pytest.mark.parametrize`.
- Edge cases: empty inputs, None, boundaries, malformed data, unexpected types.
- Property-based testing & stress testing.
- Clean assertions with clear failure messages.
