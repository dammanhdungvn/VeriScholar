import { useEffect, useRef } from "react";
import { CheckCircle2, FileText } from "lucide-react";
import { useLandingStore } from "../stores/useLandingStore";
import { MOCK_DEMO_PAPERS } from "../data/mock-papers";
import { MathRenderer } from "@/components/shared/MathRenderer";

export function DemoPaperViewer() {
  const activeCitationId = useLandingStore((s) => s.activeCitationId);
  const citationFocusTick = useLandingStore((s) => s.citationFocusTick);
  const setActiveCitation = useLandingStore((s) => s.setActiveCitation);

  // Focus 100% on the canonical Attention Is All You Need paper
  const paper = MOCK_DEMO_PAPERS[0];

  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const posEncRef = useRef<HTMLDivElement | null>(null);
  const attentionRef = useRef<HTMLDivElement | null>(null);

  // Smooth scroll and vertically center the target bounding box within the paper viewer
  useEffect(() => {
    const scrollToCitation = () => {
      const container = scrollContainerRef.current;
      if (!container || !activeCitationId) return;

      const targetEl =
        activeCitationId === "cite-pos-enc"
          ? posEncRef.current
          : activeCitationId === "cite-attention-formula"
            ? attentionRef.current
            : null;

      if (!targetEl) return;

      const containerRect = container.getBoundingClientRect();
      const targetRect = targetEl.getBoundingClientRect();

      // Absolute distance from top of scroll container's scrollable canvas
      const currentScroll = container.scrollTop;
      const targetTopInContainer = currentScroll + (targetRect.top - containerRect.top);
      const targetHeight = targetRect.height;
      const containerHeight = container.clientHeight;

      // Position the target element vertically:
      // If it fits with breathing room, center it with golden-ratio aesthetic bias
      // Otherwise align with 24px top clearance
      let desiredScroll: number;
      if (targetHeight < containerHeight - 56) {
        desiredScroll = Math.max(0, targetTopInContainer - (containerHeight - targetHeight) / 2);
      } else {
        desiredScroll = Math.max(0, targetTopInContainer - 24);
      }

      container.scrollTo({
        top: desiredScroll,
        behavior: "smooth",
      });
    };

    // Frame delay to guarantee KaTeX formula layout and web fonts are fully measured
    const timer = setTimeout(scrollToCitation, 100);
    return () => clearTimeout(timer);
  }, [activeCitationId, citationFocusTick]);

  return (
    <div className="flex flex-col h-full bg-[#faf8f4] dark:bg-[#25231f] rounded-xl border border-[#d8d3c7] dark:border-[#3a352c] overflow-hidden transition-colors duration-300 shadow-2xs dark:shadow-md">
      {/* Sleek Chrome-Style Document Tab Bar */}
      <div className="flex items-center justify-between h-9 px-3 bg-[#e8e4db] dark:bg-[#201e1a] border-b border-[#d8d3c7] dark:border-[#332e26] select-none transition-colors duration-300">
        {/* Chrome-Style Tab */}
        <div className="flex items-center">
          <div className="flex items-center gap-2 h-7 px-3 rounded-t-md bg-[#faf8f4] dark:bg-[#25231f] border-t border-x border-[#d8d3c7] dark:border-[#3a352c] text-zinc-800 dark:text-zinc-200 text-xs font-sans max-w-[220px] shadow-xs transition-colors duration-300">
            {/* Document Icon */}
            <FileText className="w-3.5 h-3.5 text-[#d97757] shrink-0" />
            <span className="truncate text-[11.5px] font-medium text-zinc-900 dark:text-zinc-100">
              Attention-Is-All-You-Need.pdf
            </span>
          </div>
        </div>

        {/* Clean Minimalist Page Counter */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-600 dark:text-zinc-400">
          <span className="w-1.5 h-1.5 rounded-full bg-[#5db872]" />
          <span>Trang 1 &amp; 6</span>
        </div>
      </div>

      {/* Realistic Academic Paper Sheet Canvas (Daylight Ivory vs Warm Slate/Charcoal Parchment) */}
      <div
        ref={scrollContainerRef}
        className="relative flex-1 p-5 sm:p-7 pb-36 sm:pb-44 overflow-y-auto overflow-x-hidden paper-scrollbar bg-[#faf8f4] dark:bg-[#25231f] text-[#1a1917] dark:text-[#ded8cc] select-text transition-colors duration-300"
      >
        {/* Academic Paper Header - Title & 8 Authors */}
        <div className="text-center pb-3 border-b border-[#e5e1d8] dark:border-[#353027] mb-4 transition-colors duration-300">
          <h3 className="font-serif text-xl sm:text-2xl font-bold text-[#11100f] dark:text-[#fbf9f5] tracking-tight leading-snug">
            Attention Is All You Need
          </h3>

          {/* 8 Authors Grid */}
          <div className="mt-2.5 text-[11px] sm:text-[11.5px] text-[#2c2a26] dark:text-[#bcb5a7] font-sans">
            <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 font-medium">
              <span>Ashish Vaswani*</span>
              <span>Noam Shazeer*</span>
              <span>Niki Parmar*</span>
              <span>Jakob Uszkoreit*</span>
              <span>Llion Jones*</span>
              <span>Aidan N. Gomez* †</span>
              <span>Łukasz Kaiser*</span>
              <span>Illia Polosukhin* ‡</span>
            </div>
            <p className="text-[10px] text-zinc-500 dark:text-zinc-400 font-mono mt-1">
              Google Brain • Google Research • University of Toronto
            </p>
          </div>

          {/* Canonical Indented Abstract */}
          <div className="max-w-[92%] sm:max-w-[86%] mx-auto mt-3.5 py-2.5 px-4 bg-[#f4efe6]/70 dark:bg-[#1f1d19] border-y border-[#e2dcd0] dark:border-[#363128] text-[11px] sm:text-[11.5px] text-justify leading-relaxed text-[#2c2a26] dark:text-[#ded8cc] italic transition-colors duration-300">
            <strong className="font-semibold not-italic text-[#141413] dark:text-[#fbf9f5]">Abstract</strong>—The
            dominant sequence transduction models are based on complex recurrent or convolutional neural networks
            in an encoder-decoder configuration. We propose the Transformer, a model architecture eschewing
            recurrence and relying entirely on attention mechanisms to draw global dependencies between input and
            output. The Transformer allows for significantly more parallelization and reaches a new state of the art.
          </div>
        </div>

        {/* 2-Column Academic Text Flow */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px] sm:text-[11.5px] leading-[1.6] text-[#2c2a26] dark:text-[#ded8cc] font-sans">
          {/* Column 1 */}
          <div className="space-y-3 text-justify">
            <p>
              <strong className="font-semibold text-[#141413] dark:text-[#fbf9f5]">1 Introduction</strong>—Recurrent
              models typically factor computation along the symbol positions of the input and output sequences.
              Aligning the positions to steps in computation time, they generate a sequence of hidden states,
              which inherently precludes parallelization within training examples.
            </p>

            {/* Section 3.5: Positional Encoding (Academic Precision Bounding Box & Highlighter) */}
            <div
              ref={posEncRef}
              data-testid="demo-bbox-highlight"
              data-active={activeCitationId === "cite-pos-enc" ? "true" : "false"}
              onClick={() => {
                const cite = paper.sample_turns[0]?.citations.find((c) => c.id === "cite-pos-enc");
                if (cite) setActiveCitation(cite);
              }}
              className={`relative p-3 rounded-[3px] transition-all duration-300 cursor-pointer overflow-visible ${
                activeCitationId === "cite-pos-enc"
                  ? "bg-[#f5a623]/12 dark:bg-[#d97757]/14 border-[1.5px] border-[#d97757] shadow-xs dark:shadow-[0_0_20px_rgba(217,119,87,0.32)] ring-1 ring-[#d97757]/20"
                  : "border-[1.5px] border-transparent hover:bg-[#d97757]/6 hover:border-[#d97757]/30"
              }`}
            >
              {/* 4 Optical Corner Crosshairs */}
              {activeCitationId === "cite-pos-enc" && (
                <>
                  <span className="absolute -top-[2px] -left-[2px] w-2.5 h-2.5 border-t-2 border-l-2 border-[#d97757] pointer-events-none" />
                  <span className="absolute -top-[2px] -right-[2px] w-2.5 h-2.5 border-t-2 border-r-2 border-[#d97757] pointer-events-none" />
                  <span className="absolute -bottom-[2px] -left-[2px] w-2.5 h-2.5 border-b-2 border-l-2 border-[#d97757] pointer-events-none" />
                  <span className="absolute -bottom-[2px] -right-[2px] w-2.5 h-2.5 border-b-2 border-r-2 border-[#d97757] pointer-events-none" />
                </>
              )}

              {/* Clean Non-overlapping Margin Chip */}
              {activeCitationId === "cite-pos-enc" && (
                <div className="flex items-center gap-1.5 pb-1 mb-1.5 border-b border-[#d97757]/25 dark:border-[#d97757]/35 text-[#c25e3e] dark:text-[#e8a55a] font-mono text-[10.5px]">
                  <CheckCircle2 className="w-3 h-3 text-[#d97757] shrink-0" />
                  <span className="font-semibold">Mục 3.5 • Tr. 6</span>
                </div>
              )}

              <p className="font-semibold text-[#121110] dark:text-[#fbf9f5] mb-1">
                3.5 Positional Encoding
              </p>
              <p>
                Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject information about the relative or absolute positions of the tokens in the sequence. To this end, we add &quot;positional encodings&quot; to the input embeddings at the bottoms of the encoder and decoder stacks:
              </p>

              {/* Dual KaTeX Formulas (Sin and Cos) */}
              <div className="my-2 p-2.5 bg-[#f2eee6] dark:bg-[#1c1a17] border border-[#dfd9cd] dark:border-[#332f27] rounded-[2px] text-center overflow-x-auto space-y-2 transition-colors duration-300">
                <MathRenderer
                  math="\text{PE}_{(\text{pos}, 2i)} = \sin\left(\frac{\text{pos}}{10000^{2i/d_{\text{model}}}}\right)"
                  block
                />
                <MathRenderer
                  math="\text{PE}_{(\text{pos}, 2i+1)} = \cos\left(\frac{\text{pos}}{10000^{2i/d_{\text{model}}}}\right)"
                  block
                />
              </div>
            </div>

            <p>
              where <MathRenderer math="pos" /> is the position and <MathRenderer math="i" /> is the dimension. That is, each dimension of the positional encoding corresponds to a sinusoid with wavelength forming a geometric progression from <MathRenderer math="2\pi" /> to <MathRenderer math="10000 \cdot 2\pi" />.
            </p>

            <p>
              <strong className="font-semibold text-[#141413] dark:text-[#fbf9f5]">4 Why Self-Attention</strong>—We compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations to another.
            </p>

            <p>
              As noted in Table 1, a self-attention layer connects all positions with a constant number of sequentially executed operations <MathRenderer math="\mathcal{O}(1)" />, whereas a recurrent layer requires <MathRenderer math="\mathcal{O}(n)" /> sequential operations.
            </p>
          </div>

          {/* Column 2 */}
          <div className="space-y-3 text-justify">
            {/* Section 3.2.1: Scaled Dot-Product Attention (Academic Precision Bounding Box) */}
            <div
              ref={attentionRef}
              data-testid="demo-bbox-highlight"
              data-active={activeCitationId === "cite-attention-formula" ? "true" : "false"}
              onClick={() => {
                const turn2 = paper.sample_turns.find((t) => t.id === "turn-2");
                const cite = turn2?.citations[0];
                if (cite) setActiveCitation(cite);
              }}
              className={`relative p-3 rounded-[3px] transition-all duration-300 cursor-pointer overflow-visible ${
                activeCitationId === "cite-attention-formula"
                  ? "bg-[#f5a623]/12 dark:bg-[#d97757]/14 border-[1.5px] border-[#d97757] shadow-xs dark:shadow-[0_0_20px_rgba(217,119,87,0.32)] ring-1 ring-[#d97757]/20"
                  : "border-[1.5px] border-transparent hover:bg-[#d97757]/6 hover:border-[#d97757]/30"
              }`}
            >
              {/* 4 Optical Corner Crosshairs */}
              {activeCitationId === "cite-attention-formula" && (
                <>
                  <span className="absolute -top-[2px] -left-[2px] w-2.5 h-2.5 border-t-2 border-l-2 border-[#d97757] pointer-events-none" />
                  <span className="absolute -top-[2px] -right-[2px] w-2.5 h-2.5 border-t-2 border-r-2 border-[#d97757] pointer-events-none" />
                  <span className="absolute -bottom-[2px] -left-[2px] w-2.5 h-2.5 border-b-2 border-l-2 border-[#d97757] pointer-events-none" />
                  <span className="absolute -bottom-[2px] -right-[2px] w-2.5 h-2.5 border-b-2 border-r-2 border-[#d97757] pointer-events-none" />
                </>
              )}

              {activeCitationId === "cite-attention-formula" && (
                <div className="flex items-center gap-1.5 pb-1 mb-1.5 border-b border-[#d97757]/25 dark:border-[#d97757]/35 text-[#c25e3e] dark:text-[#e8a55a] font-mono text-[10.5px]">
                  <CheckCircle2 className="w-3 h-3 text-[#d97757] shrink-0" />
                  <span className="font-semibold">Mục 3.2.1 • Tr. 4</span>
                </div>
              )}

              <p className="font-semibold text-[#121110] dark:text-[#fbf9f5] mb-1">
                3.2.1 Scaled Dot-Product Attention
              </p>
              <p>
                We compute the attention function on a set of queries simultaneously, packed together into a matrix <MathRenderer math="Q" />. The keys and values are also packed into matrices <MathRenderer math="K" /> and <MathRenderer math="V" />. We compute the matrix of outputs as:
              </p>

              <div className="my-2 p-2 bg-[#f2eee6] dark:bg-[#1c1a17] border border-[#dfd9cd] dark:border-[#332f27] rounded-[2px] text-center overflow-x-auto transition-colors duration-300">
                <MathRenderer
                  math="\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V"
                  block
                />
              </div>
            </div>

            <p>
              <strong className="font-semibold text-[#141413] dark:text-[#fbf9f5]">3.2.2 Multi-Head Attention</strong>—Instead of performing a single attention function with d_model-dimensional keys, values and queries, we linearly project the queries, keys and values h times.
            </p>

            <p>
              <strong className="font-semibold text-[#141413] dark:text-[#fbf9f5]">5 Training</strong>—We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs.
            </p>

            <p>
              <strong className="font-semibold text-[#141413] dark:text-[#fbf9f5]">6 Results</strong>—On the WMT 2014 English-to-German translation task, the big transformer model outperforms the best previously reported models by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4.
            </p>

            <p>
              <strong className="font-semibold text-[#141413] dark:text-[#fbf9f5]">7 Conclusion</strong>—In this work, we presented the Transformer, the first sequence transduction model based entirely on attention, replacing recurrent layers with multi-headed self-attention.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
