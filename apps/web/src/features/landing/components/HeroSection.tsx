export function HeroSection() {
  return (
    <section className="relative pt-12 pb-8 sm:pt-20 sm:pb-12 overflow-hidden">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center relative z-10">
        <div className="relative inline-block px-6 py-6 sm:px-14 sm:py-10">
          {/* Subtle 4-Corner Bounding Box Accents Synchronized with Logo */}
          <span className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-[#cc785c]/70 pointer-events-none" />
          <span className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-[#cc785c]/70 pointer-events-none" />
          <span className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-[#cc785c]/70 pointer-events-none" />
          <span className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-[#cc785c]/70 pointer-events-none" />

          {/* Slogan Quote with 2-Tone Logo Color Harmony (Veri Ink & Scholar Coral) */}
          <blockquote className="space-y-4 sm:space-y-5">
            <h1 className="font-quote text-3xl sm:text-5xl md:text-6xl font-normal leading-[1.15] text-ink tracking-tight">
              <span className="block text-ink">“What I cannot create,</span>{" "}
              <span className="block mt-1 sm:mt-2 italic bg-gradient-to-r from-[#cc785c] via-[#d97757] to-[#e8a55a] bg-clip-text text-transparent">
                I do not understand.”
              </span>
            </h1>

            {/* Author Attribution with Academic Hairline Dividers */}
            <footer className="flex items-center justify-center gap-3 pt-2 text-xs sm:text-sm font-mono text-muted uppercase tracking-[0.2em] font-medium">
              <span className="w-6 sm:w-10 h-[1px] bg-primary/40" />
              <span>Richard Feynman</span>
              <span className="w-6 sm:w-10 h-[1px] bg-primary/40" />
            </footer>
          </blockquote>
        </div>
      </div>
    </section>
  );
}
