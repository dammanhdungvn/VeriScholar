import { Sparkles, MessageSquareCode, ArrowUpRight, User } from "lucide-react";
import { useLandingStore } from "../stores/useLandingStore";
import { useDemoStream } from "../hooks/useDemoStream";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";
import { MathRenderer } from "@/components/shared/MathRenderer";

/**
 * Editorial Markdown & KaTeX Math Formatter.
 * Seamlessly parses block math $$...$$, inline math $...$, and bold text **...**
 * into high-fidelity typography without raw markup artifacts.
 */
function renderContentWithKaTeX(text: string, onCiteClick?: () => void) {
  // Split by block formulas: $$...$$
  const parts = text.split(/(\$\$[\s\S]*?\$\$)/g);

  return parts.map((part, index) => {
    if (part.startsWith("$$") && part.endsWith("$$")) {
      const math = part.slice(2, -2).trim();
      return (
        <div
          key={index}
          className="my-2.5 p-2.5 rounded-[2px] bg-[#161513] border border-[#2d2a25] text-center overflow-x-auto text-[#e8a55a]"
        >
          <MathRenderer math={math} block />
        </div>
      );
    }
    if (part.startsWith("$$")) {
      const math = part.slice(2).trim();
      if (!math) return null;
      return (
        <div
          key={index}
          className="my-2.5 p-2.5 rounded-[2px] bg-[#161513] border border-[#2d2a25] text-center overflow-x-auto text-[#e8a55a]"
        >
          <MathRenderer math={math} block />
        </div>
      );
    }

    // Split paragraphs
    const paragraphs = part.split(/\n\n+/).filter((p) => p.trim().length > 0);

    return paragraphs.map((para, pIdx) => {
      // Split tokens: **bold** or $inline_math$
      const tokens = para.split(/(\*\*[^*]+\*\*|\$[^$]+\$)/g);

      // Check if this is the last paragraph to append the subtle inline citation footnote
      const isLastPara = index === parts.length - 1 && pIdx === paragraphs.length - 1;

      return (
        <p key={`${index}-${pIdx}`} className="leading-relaxed mb-2.5 last:mb-0">
          {tokens.map((token, tIdx) => {
            if (token.startsWith("**") && token.endsWith("**")) {
              return (
                <strong key={tIdx} className="font-semibold text-zinc-100">
                  {token.slice(2, -2)}
                </strong>
              );
            }
            if (token.startsWith("$") && token.endsWith("$") && token.length > 2) {
              const inlineMath = token.slice(1, -1);
              return (
                <MathRenderer key={tIdx} math={inlineMath} className="text-[#e8a55a] px-0.5" />
              );
            }
            return token;
          })}

          {/* Perplexity-Style Inline Citation Badge */}
          {isLastPara && (
            <button
              type="button"
              onClick={onCiteClick}
              className="inline-flex items-center justify-center w-4 h-4 ml-1 rounded-full bg-[#2d2a26] hover:bg-[#3d3832] text-[#d97757] hover:text-white border border-[#44403a] text-[10px] font-mono font-bold transition-all cursor-pointer align-baseline shadow-2xs"
              title="Nhấp xem nguồn đối soát [1]"
            >
              1
            </button>
          )}
        </p>
      );
    });
  });
}

export function DemoChatPanel() {
  const activeTurnId = useLandingStore((s) => s.activeTurnId);
  const setActiveTurnId = useLandingStore((s) => s.setActiveTurnId);
  const activeCitationId = useLandingStore((s) => s.activeCitationId);
  const setActiveCitation = useLandingStore((s) => s.setActiveCitation);

  // Focus on canonical Attention paper
  const paper = MOCK_DEMO_PAPERS[0];
  const activeTurn = paper.sample_turns.find((t) => t.id === activeTurnId) || paper.sample_turns[0];

  const { displayedText, isStreaming } = useDemoStream(activeTurn.ai_answer_markdown, 10);

  // 2 Authoritative Sample Query Tabs
  const queryTabs = [
    {
      id: "turn-1",
      label: "1. RNN ở đâu?",
      citationId: "cite-pos-enc",
      inlineTag: "p. 6",
    },
    {
      id: "turn-2",
      label: "2. Công thức QKV",
      citationId: "cite-attention-formula",
      inlineTag: "p. 4",
    },
  ];

  const handleSelectTab = (tab: typeof queryTabs[0]) => {
    setActiveTurnId(tab.id);
    const targetTurn = paper.sample_turns.find((t) => t.id === tab.id);
    const cite = targetTurn?.citations.find((c) => c.id === tab.citationId) || targetTurn?.citations[0];
    if (cite) setActiveCitation(cite);
  };

  const primaryCite = activeTurn.citations[0];

  return (
    <div className="flex flex-col h-full bg-[#1c1b18] rounded-xl border border-[#33302b] overflow-hidden text-zinc-200">
      {/* Tầng 1: Fixed Editorial Header */}
      <div className="px-4 py-2.5 bg-[#22201d] border-b border-[#2d2a25] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-[#d97757]" />
          <span className="font-sans text-xs font-semibold text-zinc-100 tracking-tight">
            Socratic Copilot
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-[#5db872] animate-pulse" />
        </div>
      </div>

      {/* Tầng 2: Sample Query Tab Bar (Đồng bộ thiết kế chuẩn tab tài liệu) */}
      <div className="px-3 py-1.5 bg-[#1b1a17] border-b border-[#2d2a25] flex items-center gap-2 overflow-x-auto">
        {queryTabs.map((tab) => {
          const isSelected = activeTurn.id === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => handleSelectTab(tab)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-[4px] text-xs font-sans transition-all cursor-pointer whitespace-nowrap ${
                isSelected
                  ? "bg-[#2d2a26] text-white border border-[#44403a] shadow-2xs font-medium"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-[#252320] border border-transparent"
              }`}
            >
              <MessageSquareCode className={`w-3.5 h-3.5 ${isSelected ? "text-[#d97757]" : "text-zinc-500"}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Messages Scroll Flow */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs sm:text-sm">
        {/* User Query Box */}
        <div className="p-3 rounded-[2px] bg-[#22201d] border border-[#2e2a24]">
          <div className="flex items-center gap-1.5 text-[10.5px] font-mono text-zinc-400 uppercase tracking-wider mb-1">
            <User className="w-3 h-3 text-primary" />
            <span>Bạn</span>
          </div>
          <p className="text-zinc-100 font-sans leading-relaxed text-[12.5px]">
            {activeTurn.user_query}
          </p>
        </div>

        {/* AI Response Container */}
        <div className="p-3.5 rounded-[2px] bg-[#1e1c19] border border-[#302d27] space-y-3">
          {/* Socratic Presupposition Validation Banner */}
          {activeTurn.ai_thought && (
            <div className="p-2.5 rounded-[2px] bg-[#d97757]/8 border-l-[2.5px] border-[#d97757] text-xs">
              <div className="flex items-center gap-1.5 font-sans font-semibold text-[#e8a55a] mb-1">
                <Sparkles className="w-3 h-3 text-[#e8a55a] shrink-0" />
                <span>Socratic Fact-Check: Phát hiện sai lệch tiền đề</span>
              </div>
              <p className="text-zinc-300 italic text-[11.5px] leading-relaxed">
                {activeTurn.ai_thought}
              </p>
            </div>
          )}

          {/* Formatted Answer with KaTeX Typesetting & Inline Footnote */}
          <div className="font-sans text-xs sm:text-[13px] text-zinc-200 leading-[1.6]">
            {renderContentWithKaTeX(
              displayedText,
              () => primaryCite && setActiveCitation(primaryCite)
            )}
            {isStreaming && (
              <span className="inline-block w-1.5 h-3.5 bg-[#d97757] ml-0.5 animate-pulse align-middle" />
            )}
          </div>

          {/* Perplexity-Style Sources Card */}
          {primaryCite && (
            <div className="pt-2.5 border-t border-[#292621]">
              <div className="text-[10.5px] font-sans font-medium text-zinc-400 mb-1.5 flex items-center gap-1.5">
                <span>Nguồn đối soát</span>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  data-testid="demo-citation-badge"
                  onClick={() => setActiveCitation(primaryCite)}
                  onMouseEnter={() => setActiveCitation(primaryCite)}
                  className={`group flex items-center gap-2.5 px-2.5 py-1.5 rounded-md transition-all text-left cursor-pointer border ${
                    activeCitationId === primaryCite.id
                      ? "bg-[#2c2823] border-[#d97757] shadow-xs"
                      : "bg-[#201e1b] hover:bg-[#272420] border-[#33302a] hover:border-[#443f36]"
                  }`}
                  title="Nhấp để định vị trên bài báo gốc"
                >
                  {/* Perplexity numbered badge */}
                  <div
                    className={`w-5 h-5 rounded flex items-center justify-center shrink-0 text-[10.5px] font-mono font-bold ${
                      activeCitationId === primaryCite.id
                        ? "bg-[#d97757] text-white"
                        : "bg-[#2a2723] text-[#d97757] border border-[#3e3931]"
                    }`}
                  >
                    1
                  </div>

                  <div className="min-w-0 pr-1">
                    <div className="text-[11.5px] font-medium text-zinc-200 group-hover:text-white truncate max-w-[200px]">
                      Attention Is All You Need
                    </div>
                    <div className="text-[10px] text-zinc-400 truncate font-mono">
                      {activeTurn.id === "turn-1"
                        ? "Mục 3.5 (Trang 6) • Vaswani et al."
                        : "Mục 3.2.1 (Trang 4) • Vaswani et al."}
                    </div>
                  </div>

                  <ArrowUpRight
                    className={`w-3.5 h-3.5 shrink-0 transition-colors ${
                      activeCitationId === primaryCite.id
                        ? "text-[#d97757]"
                        : "text-zinc-500 group-hover:text-zinc-300"
                    }`}
                  />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
