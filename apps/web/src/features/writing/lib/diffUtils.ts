/**
 * LCS-based visual line difference calculation for Suggestion Review Panel.
 */

export interface DiffLine {
  type: "added" | "removed" | "unchanged";
  text: string;
}

export function computeSimpleDiff(original: string, suggested: string): DiffLine[] {
  const origLines = original ? original.split("\n") : [];
  const suggLines = suggested ? suggested.split("\n") : [];

  if (origLines.length === 0) {
    return suggLines.map((line) => ({ type: "added", text: line }));
  }
  if (suggLines.length === 0) {
    return origLines.map((line) => ({ type: "removed", text: line }));
  }

  const dp: number[][] = Array.from({ length: origLines.length + 1 }, () =>
    new Array(suggLines.length + 1).fill(0)
  );

  for (let i = 0; i < origLines.length; i++) {
    for (let j = 0; j < suggLines.length; j++) {
      if (origLines[i] === suggLines[j]) {
        dp[i + 1][j + 1] = dp[i][j] + 1;
      } else {
        dp[i + 1][j + 1] = Math.max(dp[i + 1][j], dp[i][j + 1]);
      }
    }
  }

  let i = origLines.length;
  let j = suggLines.length;
  const result: DiffLine[] = [];

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && origLines[i - 1] === suggLines[j - 1]) {
      result.unshift({ type: "unchanged", text: origLines[i - 1] });
      i--;
      j--;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.unshift({ type: "added", text: suggLines[j - 1] });
      j--;
    } else if (i > 0 && (j === 0 || dp[i][j - 1] < dp[i - 1][j])) {
      result.unshift({ type: "removed", text: origLines[i - 1] });
      i--;
    }
  }

  return result;
}

export interface RebasedRangeResult {
  start: number;
  end: number;
  hasConflict: boolean;
}

/**
 * Calculates rebased start and end character offsets in currentContent for an edit that was
 * originally planned at [originalStart, originalEnd] in baseContent.
 *
 * Guarantees that:
 * 1. Edits typed before originalStart cleanly shift the insertion range forward.
 * 2. Edits typed after originalEnd do not alter the insertion range.
 * 3. Deletions before originalStart cleanly shift the insertion range backward.
 * 4. User unpersisted edits are strictly preserved without being truncated or overwritten.
 */
export function calculateRebasedRange(
  baseContent: string,
  currentContent: string,
  originalStart: number,
  originalEnd: number,
  originalText?: string
): RebasedRangeResult {
  // 1. Identical content: zero drift
  if (baseContent === currentContent) {
    const start = Math.min(Math.max(0, originalStart), currentContent.length);
    const end = Math.min(Math.max(start, originalEnd), currentContent.length);
    return { start, end, hasConflict: false };
  }

  const safeOriginalStart = Math.min(Math.max(0, originalStart), baseContent.length);
  const safeOriginalEnd = Math.min(Math.max(safeOriginalStart, originalEnd), baseContent.length);
  const targetText =
    originalText !== undefined ? originalText : baseContent.slice(safeOriginalStart, safeOriginalEnd);

  // 2. Edit happened strictly AFTER a non-empty target range:
  // Prefix of baseContent up to safeOriginalEnd matches the start of currentContent
  if (
    safeOriginalEnd > safeOriginalStart &&
    currentContent.length >= safeOriginalEnd &&
    currentContent.slice(0, safeOriginalEnd) === baseContent.slice(0, safeOriginalEnd)
  ) {
    return { start: safeOriginalStart, end: safeOriginalEnd, hasConflict: false };
  }

  // 3. Edit happened strictly BEFORE the target range:
  // Suffix of baseContent from safeOriginalEnd matches the tail of currentContent
  const suffix = baseContent.slice(safeOriginalEnd);
  const delta = currentContent.length - baseContent.length;
  const shiftedStart = safeOriginalStart + delta;
  const shiftedEnd = safeOriginalEnd + delta;

  if (
    shiftedStart >= 0 &&
    shiftedEnd <= currentContent.length &&
    (suffix.length === 0 || currentContent.slice(shiftedEnd) === suffix) &&
    (targetText.length === 0 || currentContent.slice(shiftedStart, shiftedEnd) === targetText)
  ) {
    return { start: shiftedStart, end: shiftedEnd, hasConflict: false };
  }

  // 4. Try to locate targetText if non-empty
  if (targetText.length > 0) {
    // Check at shiftedStart first
    if (
      shiftedStart >= 0 &&
      shiftedStart + targetText.length <= currentContent.length &&
      currentContent.slice(shiftedStart, shiftedStart + targetText.length) === targetText
    ) {
      return { start: shiftedStart, end: shiftedStart + targetText.length, hasConflict: false };
    }

    // Check at safeOriginalStart
    if (
      safeOriginalStart + targetText.length <= currentContent.length &&
      currentContent.slice(safeOriginalStart, safeOriginalStart + targetText.length) === targetText
    ) {
      return { start: safeOriginalStart, end: safeOriginalStart + targetText.length, hasConflict: false };
    }

    // Find all occurrences of targetText in currentContent
    const allOccurrences: number[] = [];
    let idx = currentContent.indexOf(targetText);
    while (idx !== -1) {
      allOccurrences.push(idx);
      idx = currentContent.indexOf(targetText, idx + 1);
    }

    if (allOccurrences.length > 0) {
      const preferredPos = shiftedStart >= 0 ? shiftedStart : safeOriginalStart;
      let closestIdx = allOccurrences[0];
      let minDiff = Math.abs(closestIdx - preferredPos);
      for (const pos of allOccurrences) {
        const diff = Math.abs(pos - preferredPos);
        if (diff < minDiff) {
          minDiff = diff;
          closestIdx = pos;
        }
      }
      return { start: closestIdx, end: closestIdx + targetText.length, hasConflict: false };
    }
  }

  // 5. Fallback for cursor position / modified selection: calculate common prefix length
  let commonPrefixLen = 0;
  while (
    commonPrefixLen < baseContent.length &&
    commonPrefixLen < currentContent.length &&
    baseContent[commonPrefixLen] === currentContent[commonPrefixLen]
  ) {
    commonPrefixLen++;
  }

  if (commonPrefixLen <= safeOriginalStart) {
    const newStart = Math.min(Math.max(commonPrefixLen, shiftedStart), currentContent.length);
    const newEnd = Math.min(newStart + (safeOriginalEnd - safeOriginalStart), currentContent.length);
    const hasConflict = targetText.length > 0 && currentContent.slice(newStart, newEnd) !== targetText;
    return { start: newStart, end: newEnd, hasConflict };
  }

  return { start: safeOriginalStart, end: safeOriginalEnd, hasConflict: true };
}

