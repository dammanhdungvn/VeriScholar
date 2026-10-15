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
