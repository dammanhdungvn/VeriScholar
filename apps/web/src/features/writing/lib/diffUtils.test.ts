import { describe, it, expect } from "vitest";
import { computeSimpleDiff } from "./diffUtils";

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
