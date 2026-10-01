# AI Guardrails Specification for VeriScholar

This document details the 3 runtime security layers protecting VeriScholar from adversarial attacks, prompt injections, and hallucinations.

---

## 1. Threat Model & Vectors

| Threat Vector | Description | Defense Layer |
| :--- | :--- | :--- |
| **Direct Prompt Injection** | Commands like "Ignore previous instructions", "Disregard all rules" | Input Guardrail (`scan_user_input`) |
| **Persona Hijacking** | Forcing roles like DAN, uncensored bot, or evil AI | Input Guardrail (`JAILBREAK_PERSONA`) |
| **Prompt Exfiltration** | Queries asking to "repeat your system prompt verbatim" | Input Guardrail (`PROMPT_LEAKAGE`) |
| **Context Delimiter Breakout** | Attempting to close XML tags (`</untrusted_document_context>`) | Input Guardrail & Sanitizer |
| **Indirect Injections in PDF** | Adversarial text hidden inside uploaded academic PDF chunks | Context Sandboxing (CDATA + Delimiter Neutralizer) |
| **Citation Hallucination** | LLM inventing fake citations like `[^cit_99]` | Output Guardrail (`verify_output_grounding`) |
| **System Leakage in Output** | LLM inadvertently echoing system directives in answers | Output Guardrail (`has_system_leak`) |

---

## 2. Architecture & Implementation

### 2.1. Layer 1: Input Guardrail (`AIGuardrailsService.scan_user_input`)
- Scans `request.question` against compiled heuristic signatures and length constraints ($L \le 4000$).
- If unsafe:
  - Emits SSE reasoning event detailing violation type.
  - Emits polite refusal token: *"Yêu cầu chứa chỉ thị thay đổi hành vi hệ thống... VeriScholar chỉ giải đáp câu hỏi học thuật có căn cứ từ tài liệu."*
  - Emits `done` event with `finish_reason: "blocked_by_guardrail"`.
  - Persists turn into database with `finish_reason == "blocked_by_guardrail"`.
  - Short-circuits execution before invoking LLM or incurring API costs.

### 2.2. Layer 2: Context Sandboxing (`AIGuardrailsService.build_sandboxed_context`)
- All external PDF chunk content is encapsulated in:
  ```xml
  <untrusted_document_context>
    <evidence_chunk id="cit_1" page="3" title="...">
      <![CDATA[
      [Extracted chunk content with ']]>' neutralized to ']] >']
      ]]>
    </evidence_chunk>
  </untrusted_document_context>
  ```
- Prepends `AIGuardrailsService.get_security_directive()` establishing strict persona boundaries (passive data invariant, zero override).

### 2.3. Layer 3: Output Guardrail (`AIGuardrailsService.verify_output_grounding`)
- Extracts all citation tags matching `\[\^?(cit_[a-zA-Z0-9_\-]+)\]`.
- Validates against active `citations` in the session.
- Automatically strips hallucinated citations from the final persisted answer and logs warnings.
- Checks for system prompt leakage.
