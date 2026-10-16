/**
 * Helper to construct a surrounding context window buffer (<pre_context>, <target_selection>, <post_context>)
 * for Zero-Click Focus from Editor Selection to Writing Assistant Chat.
 */
export function buildSelectionContextBuffer(
  content: string,
  start: number,
  end: number,
  windowChars = 300
): string {
  const pre = content.substring(Math.max(0, start - windowChars), start);
  const target = content.substring(start, end);
  const post = content.substring(end, Math.min(content.length, end + windowChars));

  return `<pre_context>\n${pre.trim()}\n</pre_context>\n<target_selection>\n${target.trim()}\n</target_selection>\n<post_context>\n${post.trim()}\n</post_context>`;
}
