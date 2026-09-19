import { AtmosphericBackground } from "./AtmosphericBackground";
import { LandingNavbar } from "./LandingNavbar";
import { HeroSection } from "./HeroSection";
import { InteractiveDemo } from "./InteractiveDemo";
import { LandingFooter } from "./LandingFooter";
import { QuickUploadModal } from "./QuickUploadModal";

export function LandingPageContainer() {
  return (
    <div className="relative min-h-screen bg-canvas text-ink flex flex-col font-sans selection:bg-primary/20 selection:text-ink">
      {/* Interactive Atmospheric Constellation & Perspective Grid Background */}
      <AtmosphericBackground />

      {/* Top Fixed Sticky Navigation */}
      <LandingNavbar />

      {/* Main Editorial Streamlined Content */}
      <main className="flex-1 relative z-10">
        {/* Band 1: Ultra-Clean Production Hero */}
        <HeroSection />

        {/* Band 2: Mac Studio Interactive Demo & 3 Core Keyword Feature Cards */}
        <InteractiveDemo />
      </main>

      {/* Closing Editorial Footer */}
      <LandingFooter />

      {/* Global Quick Upload Modal */}
      <QuickUploadModal />
    </div>
  );
}
