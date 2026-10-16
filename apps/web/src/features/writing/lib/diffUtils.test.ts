import { describe, it, expect } from "vitest";
import { computeSimpleDiff, calculateRebasedRange } from "./diffUtils";

describe("computeSimpleDiff", () => {
  it("returns all added lines when original is empty", () => {
    const original = "";
    const suggested = "Line 1\nLine 2";
    const diff = computeSimpleDiff(original, suggested);

    expect(diff).toEqual([
      { type: "added", text: "Line 1" },
      { type: "added", text: "Line 2" },
    ]);
  });

  it("returns all removed lines when suggested is empty", () => {
    const original = "Line 1\nLine 2";
    const suggested = "";
    const diff = computeSimpleDiff(original, suggested);

    expect(diff).toEqual([
      { type: "removed", text: "Line 1" },
      { type: "removed", text: "Line 2" },
    ]);
  });

  it("identifies identical lines as unchanged", () => {
    const original = "Line A\nLine B";
    const suggested = "Line A\nLine B";
    const diff = computeSimpleDiff(original, suggested);

    expect(diff).toEqual([
      { type: "unchanged", text: "Line A" },
      { type: "unchanged", text: "Line B" },
    ]);
  });

  it("identifies added and removed lines correctly", () => {
    const original = "Intro\nOld body\nOutro";
    const suggested = "Intro\nNew body\nOutro";
    const diff = computeSimpleDiff(original, suggested);

    expect(diff).toEqual([
      { type: "unchanged", text: "Intro" },
      { type: "removed", text: "Old body" },
      { type: "added", text: "New body" },
      { type: "unchanged", text: "Outro" },
    ]);
  });

  it("handles insertions and deletions cleanly", () => {
    const original = "A\nC";
    const suggested = "A\nB\nC\nD";
    const diff = computeSimpleDiff(original, suggested);

    expect(diff).toEqual([
      { type: "unchanged", text: "A" },
      { type: "added", text: "B" },
      { type: "unchanged", text: "C" },
      { type: "added", text: "D" },
    ]);
  });
});

describe("calculateRebasedRange", () => {
  it("returns original range when baseContent equals currentContent", () => {
    const base = "Hello world from VeriScholar";
    const res = calculateRebasedRange(base, base, 6, 11, "world");
    expect(res).toEqual({ start: 6, end: 11, hasConflict: false });
  });

  it("shifts range forward when text is typed before the selection", () => {
    const base = "Transformers replace recurrent networks completely.";
    // "recurrent networks" is at index [21, 39]
    const origStart = base.indexOf("recurrent networks");
    const origEnd = origStart + "recurrent networks".length;

    // User types "Recent " (7 chars) at position 0
    const current = "Recent " + base;
    const res = calculateRebasedRange(base, current, origStart, origEnd, "recurrent networks");

    expect(res.start).toBe(origStart + 7);
    expect(res.end).toBe(origEnd + 7);
    expect(res.hasConflict).toBe(false);
    expect(current.slice(res.start, res.end)).toBe("recurrent networks");
  });

  it("keeps range unchanged when text is typed after the selection", () => {
    const base = "Transformers replace recurrent networks completely.";
    const origStart = base.indexOf("recurrent networks");
    const origEnd = origStart + "recurrent networks".length;

    // User types text at the end
    const current = base + "\n\\section{Methods}";
    const res = calculateRebasedRange(base, current, origStart, origEnd, "recurrent networks");

    expect(res.start).toBe(origStart);
    expect(res.end).toBe(origEnd);
    expect(res.hasConflict).toBe(false);
    expect(current.slice(res.start, res.end)).toBe("recurrent networks");
  });

  it("shifts range backward when text before selection is deleted", () => {
    const base = "Deep neural transformers replace recurrent networks.";
    const origStart = base.indexOf("recurrent networks");
    const origEnd = origStart + "recurrent networks".length;

    // User deleted "Deep neural " (12 chars)
    const current = "transformers replace recurrent networks.";
    const res = calculateRebasedRange(base, current, origStart, origEnd, "recurrent networks");

    expect(res.start).toBe(origStart - 12);
    expect(res.end).toBe(origEnd - 12);
    expect(res.hasConflict).toBe(false);
    expect(current.slice(res.start, res.end)).toBe("recurrent networks");
  });

  it("handles cursor insertion rebase when user typed before cursor", () => {
    const base = "\\section{Intro}\n";
    const cursor = base.length; // cursor at 16

    // User typed "Some intro text."
    const current = base + "Some intro text.";
    const res = calculateRebasedRange(base, current, cursor, cursor, "");

    expect(res.start).toBe(current.length);
    expect(res.end).toBe(current.length);
    expect(res.hasConflict).toBe(false);
  });

  it("detects conflict when the target selection itself was modified", () => {
    const base = "The model achieved 95% accuracy.";
    const origStart = base.indexOf("95% accuracy");
    const origEnd = origStart + "95% accuracy".length;

    // User modified the selection to "98% top-1 accuracy"
    const current = "The model achieved 98% top-1 accuracy.";
    const res = calculateRebasedRange(base, current, origStart, origEnd, "95% accuracy");

    expect(res.hasConflict).toBe(true);
  });

  it("enforces proximity threshold for short keywords (length <= 4) and flags conflict when distance > 40 (FINDING-DEFECT-01-03)", () => {
    // Target short keyword "the" at index 100 in baseContent
    const padding = "A".repeat(96) + " on "; // 100 chars
    const base = "the first intro. " + padding + "the table was wooden.";
    const target = "the";
    const secondTheIndex = base.indexOf("the table");
    const origStart = secondTheIndex;
    const origEnd = secondTheIndex + target.length;

    // User deletes the second occurrence and types "a desk was wooden."
    // current has only the first "the" at position 0, which is > 40 chars away
    const current = "the first intro. " + padding + "a desk was wooden.";
    const res = calculateRebasedRange(base, current, origStart, origEnd, target);

    expect(res.hasConflict).toBe(true);
  });

  it("permits short keywords when occurrence is within proximity threshold (<= 40 chars) (FINDING-DEFECT-01-03)", () => {
    const base = "We use the model.";
    const origStart = base.indexOf("the");
    const origEnd = origStart + "the".length;

    // User types "Indeed, " (8 chars) at the start
    const current = "Indeed, We use the model.";
    const res = calculateRebasedRange(base, current, origStart, origEnd, "the");

    expect(res.hasConflict).toBe(false);
    expect(res.start).toBe(origStart + 8);
    expect(current.slice(res.start, res.end)).toBe("the");
  });

  it("enforces proximity threshold for longer keywords (length > 4) when distance > 120 chars (FINDING-DEFECT-01-03)", () => {
    const base = "transformer at start. " + "x".repeat(200) + " transformer at distant end.";
    const target = "transformer";
    const distantStart = base.lastIndexOf("transformer");
    const distantEnd = distantStart + target.length;

    // Delete the distant transformer
    const current = "transformer at start. " + "x".repeat(200) + " something else at distant end.";
    const res = calculateRebasedRange(base, current, distantStart, distantEnd, target);

    expect(res.hasConflict).toBe(true);
  });
});

