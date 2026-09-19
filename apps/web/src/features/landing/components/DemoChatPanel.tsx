import * as React from "react";
import { Sparkles, ArrowUp, User, RotateCcw, Plus, Mic, Headphones } from "lucide-react";
import { useLandingStore } from "../stores/useLandingStore";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";
import { MathRenderer } from "@/components/shared/MathRenderer";

/**
 * Editorial Markdown & KaTeX Math Formatter.
 * Parses block math $$...$$, inline math $...$, and bold text **...**
 * into high-fidelity typography without raw markup artifacts.
 */
function renderParagraphs(text: string, isLastBlock: boolean, onCiteClick?: () => void) {
  const paras = text.split(/\n\n+/).filter((p) => p.trim().length > 0);

  return paras.map((para, pIdx) => {
    const isVeryLast = isLastBlock && pIdx === paras.length - 1;
    const tokens = para.split(/(\*\*[^*]+\*\*|\$[^$]+\$)/g);

    return (
      <p key={pIdx} className="leading-relaxed mb-2.5 last:mb-0 text-zinc-200">
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

        {isVeryLast && onCiteClick && (
          <button
            type="button"
            data-testid="demo-citation-badge"
            onClick={onCiteClick}
            className="inline-flex items-center justify-center w-4 h-4 ml-1.5 rounded-full bg-[#2d2a26] hover:bg-[#d97757] text-[#d97757] hover:text-white border border-[#44403a] text-[10px] font-mono font-bold transition-all cursor-pointer align-baseline shadow-2xs"
            title="Nhấp để định vị Bounding Box trên trang 6 bài báo gốc"
          >
            1
          </button>
        )}
      </p>
    );
  });
}

function renderContentWithKaTeX(text: string, onCiteClick?: () => void) {
  if (text.includes("$$")) {
    const parts = text.split("$$");
    const beforeText = parts[0];
    const mathFormula = parts[1];
    const afterText = parts.slice(2).join("$$");

    return (
      <div className="space-y-2.5">
        {renderParagraphs(beforeText, false, undefined)}

        {mathFormula && (
          <div className="my-2 p-2.5 rounded-lg bg-[#141311] border border-[#2b2721] text-center overflow-hidden text-[#e8a55a] shadow-inner">
            <MathRenderer math={mathFormula.trim()} block />
          </div>
        )}

        {afterText && renderParagraphs(afterText, true, onCiteClick)}
      </div>
    );
  }

  return renderParagraphs(text, true, onCiteClick);
}

const CANONICAL_PROMPT =
  "Làm thế nào Transformer xử lý được thứ tự từ trong câu khi loại bỏ hoàn toàn mạng đệ quy (RNN)?";

export function DemoChatPanel() {
  const setActiveCitation = useLandingStore((s) => s.setActiveCitation);

  const paper = MOCK_DEMO_PAPERS[0];
  const activeTurn = paper.sample_turns[0];
  const primaryCite = activeTurn.citations[0];

  // States for web-video simulation
  const [inputVal, setInputVal] = React.useState("");
  const [userMessage, setUserMessage] = React.useState<string | null>(null);
  const [isTyping, setIsTyping] = React.useState(false);
  const [isSubmitAnimating, setIsSubmitAnimating] = React.useState(false);
  const [isThinking, setIsThinking] = React.useState(false);
  const [aiResponseVisible, setAiResponseVisible] = React.useState(false);
  const [displayedText, setDisplayedText] = React.useState("");
  const [isStreaming, setIsStreaming] = React.useState(false);

  const chatScrollRef = React.useRef<HTMLDivElement | null>(null);
  const messagesEndRef = React.useRef<HTMLDivElement | null>(null);
  const inputRef = React.useRef<HTMLInputElement | null>(null);
  const timersRef = React.useRef<ReturnType<typeof setTimeout>[]>([]);
  const streamIntervalRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  // Auto-scroll chat to bottom continuously as text streams or messages change
  React.useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [displayedText, userMessage, isThinking, isStreaming]);

  // Keep input scroll offset tracking typing cursor during auto-type simulation
  React.useEffect(() => {
    if (inputRef.current) {
      inputRef.current.scrollLeft = inputRef.current.scrollWidth;
    }
  }, [inputVal]);

  const clearAllTimers = React.useCallback(() => {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
  }, []);

  // Main simulation lifecycle
  const runSimulation = React.useCallback(() => {
    clearAllTimers();

    // 1. Reset state
    setInputVal("");
    setUserMessage(null);
    setIsTyping(true);
    setIsSubmitAnimating(false);
    setIsThinking(false);
    setAiResponseVisible(false);
    setDisplayedText("");
    setIsStreaming(false);

    // Initial brief delay before starting typing (300ms)
    const promptChars = CANONICAL_PROMPT.split("");
    let charIdx = 0;

    const startTypingTimeout = setTimeout(() => {
      const typingInterval = setInterval(() => {
        charIdx++;
        setInputVal(CANONICAL_PROMPT.slice(0, charIdx));

        if (charIdx >= promptChars.length) {
          clearInterval(typingInterval);
          setIsTyping(false);

          // 2. Pause briefly as if about to press Enter (350ms)
          const submitAnimTimeout = setTimeout(() => {
            setIsSubmitAnimating(true);

            // 3. Trigger Enter / Submit (250ms press animation)
            const enterTimeout = setTimeout(() => {
              setIsSubmitAnimating(false);
              setUserMessage(CANONICAL_PROMPT);
              setInputVal("");
              setIsThinking(true);

              // 4. AI Thinking Phase (~1.4s thinking)
              const thinkingTimeout = setTimeout(() => {
                setIsThinking(false);
                setAiResponseVisible(true);
                setIsStreaming(true);

                // Automatically highlight the Visual Grounding Bounding Box on the PDF
                if (primaryCite) {
                  setActiveCitation(primaryCite);
                }

                // 5. Stream AI Response text smoothly
                const fullText = activeTurn.ai_answer_markdown;
                let streamIndex = 0;
                streamIntervalRef.current = setInterval(() => {
                  streamIndex += 10;
                  if (streamIndex >= fullText.length) {
                    setDisplayedText(fullText);
                    setIsStreaming(false);
                    if (streamIntervalRef.current) {
                      clearInterval(streamIntervalRef.current);
                      streamIntervalRef.current = null;
                    }
                  } else {
                    setDisplayedText(fullText.slice(0, streamIndex));
                  }
                }, 16);
              }, 1400);

              timersRef.current.push(thinkingTimeout);
            }, 250);

            timersRef.current.push(enterTimeout);
          }, 350);

          timersRef.current.push(submitAnimTimeout);
        }
      }, 20);
    }, 300);

    timersRef.current.push(startTypingTimeout);
  }, [clearAllTimers, activeTurn.ai_answer_markdown, primaryCite, setActiveCitation]);

  // Trigger simulation automatically when component mounts or user refreshes page
  React.useEffect(() => {
    const timer = setTimeout(() => {
      runSimulation();
    }, 100);
    return () => {
      clearTimeout(timer);
      clearAllTimers();
    };
  }, [runSimulation, clearAllTimers]);

  return (
    <div
      data-testid="demo-chat-panel"
      data-streaming={isStreaming ? "true" : "false"}
      className="flex flex-col h-full bg-[#1c1b18] rounded-xl border border-[#33302b] overflow-hidden text-zinc-200 shadow-xl"
    >
      {/* Editorial Header with Clean Title & Replay Button */}
      <div className="px-4 py-3 bg-[#201e1a] border-b border-[#2d2923] flex items-center justify-between select-none shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-[#d97757]/15 border border-[#d97757]/30 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-[#d97757]" />
          </div>
          <span className="font-sans text-xs font-semibold text-zinc-100 tracking-tight">
            Socratic Copilot
          </span>
        </div>

        {/* Replay Demo Action Button */}
        <button
          type="button"
          onClick={runSimulation}
          className="p-1.5 rounded-md text-zinc-400 hover:text-zinc-100 hover:bg-[#2c2822] border border-transparent hover:border-[#3d3830] transition-all cursor-pointer"
          title="Xem lại demo tự động"
          aria-label="Xem lại demo tự động"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Messages Flow: Generous Horizontal Alignment without awkward scrollbars */}
      <div
        ref={chatScrollRef}
        className="flex-1 p-3.5 sm:p-4.5 overflow-y-auto overflow-x-hidden scrollbar-none space-y-3.5 text-xs sm:text-[12.5px]"
      >
        {/* 1. USER PROMPT: Horizontal Layout with [Text Bubble] [User Avatar] */}
        {userMessage && (
          <div className="flex items-start justify-end gap-2.5 ml-auto max-w-[88%] sm:max-w-[84%]">
            <div className="p-3 sm:p-3.5 rounded-2xl rounded-tr-xs bg-[#2c2822] border border-[#3e3830] text-[#f7f5f0] shadow-sm font-sans text-xs sm:text-[13px] leading-relaxed">
              {userMessage}
            </div>
            <div
              className="w-7 h-7 rounded-full bg-[#38332a] border border-[#4d4538] flex items-center justify-center shrink-0 text-[#d97757] mt-0.5 shadow-xs"
              title="Bạn"
            >
              <User className="w-3.5 h-3.5" />
            </div>
          </div>
        )}

        {/* 2. AI THINKING: Minimalist Pulsing Indicator */}
        {isThinking && (
          <div className="flex items-start gap-2.5 mr-auto w-full">
            <div className="w-7 h-7 rounded-full bg-[#d97757]/15 border border-[#d97757]/30 flex items-center justify-center shrink-0 text-[#d97757] mt-0.5">
              <Sparkles className="w-3.5 h-3.5 animate-spin" />
            </div>
            <div className="p-3 rounded-2xl rounded-tl-xs bg-[#1f1d19] border border-[#302c25] text-xs text-zinc-400 flex items-center gap-2">
              <div className="w-3.5 h-3.5 rounded-full border-2 border-[#d97757] border-t-transparent animate-spin shrink-0" />
              <span>Đang đối soát nội dung với bài báo Attention Is All You Need...</span>
            </div>
          </div>
        )}

        {/* 3. AI RESPONSE: Horizontal Layout with [AI Avatar] [AI Bubble] */}
        {aiResponseVisible && (
          <div className="flex items-start gap-2.5 mr-auto w-full">
            <div className="w-7 h-7 rounded-full bg-[#d97757]/15 border border-[#d97757]/30 flex items-center justify-center shrink-0 text-[#d97757] mt-0.5 shadow-xs">
              <Sparkles className="w-3.5 h-3.5" />
            </div>

            <div className="flex-1 p-3.5 sm:p-4 rounded-2xl rounded-tl-xs bg-[#1e1c18] border border-[#332f27] space-y-2.5 shadow-sm text-zinc-200">
              {/* Formatted Answer with KaTeX Typesetting & Inline Footnote [1] */}
              <div className="font-sans text-xs sm:text-[13px] text-zinc-200 leading-[1.6]">
                {renderContentWithKaTeX(
                  displayedText,
                  () => primaryCite && setActiveCitation(primaryCite)
                )}
                {isStreaming && (
                  <span className="inline-block w-1.5 h-3.5 bg-[#d97757] ml-0.5 animate-pulse align-middle" />
                )}
              </div>
            </div>
          </div>
        )}

        {/* Breathing cushion and scroll anchor */}
        <div ref={messagesEndRef} className="h-4 shrink-0" />
      </div>

      {/* Docked Chat Input Bar: Strictly Display/Simulation Mode (No manual input/enter allowed) */}
      <div className="p-2.5 sm:p-3 bg-[#181715] border-t border-[#2d2923] shrink-0">
        <div className="relative">
          <div
            className={`flex items-center gap-2 px-2.5 sm:px-3 py-2 sm:py-2.5 rounded-xl bg-[#211f1b] border transition-all duration-300 shadow-inner select-none cursor-default ${
              isTyping
                ? "border-[#d97757]/70 shadow-[0_0_14px_rgba(217,119,87,0.22)] ring-1 ring-[#d97757]/30"
                : "border-[#38342c]"
            }`}
          >
            {/* Left Icon: Plus (+) */}
            <button
              type="button"
              tabIndex={-1}
              aria-label="Thêm tập tin hoặc đính kèm"
              title="Thêm tập tin hoặc đính kèm"
              className="w-7 h-7 rounded-lg flex items-center justify-center text-zinc-400 hover:text-zinc-200 transition-colors shrink-0 cursor-default pointer-events-none select-none"
            >
              <Plus className="w-4 h-4" />
            </button>

            <input
              ref={inputRef}
              type="text"
              value={inputVal}
              readOnly
              tabIndex={-1}
              onKeyDown={(e) => e.preventDefault()}
              placeholder={
                isTyping
                  ? ""
                  : isThinking
                  ? "Đang đối soát nội dung với bài báo Attention Is All You Need..."
                  : isStreaming
                  ? "Socratic Copilot đang phân tích đối soát..."
                  : "Mô phỏng tự động • Nhấp ↺ trên góc phải để phát lại"
              }
              className="flex-1 min-w-0 bg-transparent border-none outline-none text-zinc-200 text-xs sm:text-[13px] placeholder:text-zinc-500 font-sans cursor-default pointer-events-none select-none"
            />

            {/* Right Action Icons: Dictate & Voice mode when empty; Orange Arrow button when typing */}
            {inputVal.length > 0 ? (
              <button
                type="button"
                tabIndex={-1}
                aria-label="Gửi câu hỏi"
                title="Gửi câu hỏi"
                className={`w-7 h-7 rounded-lg flex items-center justify-center bg-[#d97757] border border-[#d97757] text-white shadow-xs transition-all pointer-events-none shrink-0 ${
                  isSubmitAnimating ? "scale-90 bg-[#c56646]" : ""
                }`}
              >
                <ArrowUp className="w-3.5 h-3.5 text-white stroke-[2.5]" />
              </button>
            ) : (
              <div className="flex items-center gap-1 shrink-0 select-none">
                <button
                  type="button"
                  tabIndex={-1}
                  aria-label="Dictate"
                  title="Dictate"
                  className="w-7 h-7 rounded-lg flex items-center justify-center text-zinc-400 hover:text-zinc-200 transition-colors cursor-default pointer-events-none"
                >
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  tabIndex={-1}
                  aria-label="Use voice mode"
                  title="Use voice mode"
                  className="w-7 h-7 rounded-lg flex items-center justify-center text-zinc-400 hover:text-zinc-200 transition-colors cursor-default pointer-events-none"
                >
                  <Headphones className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
