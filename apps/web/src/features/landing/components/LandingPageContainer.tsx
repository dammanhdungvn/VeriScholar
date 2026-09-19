import { AtmosphericBackground } from "./AtmosphericBackground";
import { LandingNavbar } from "./LandingNavbar";
import { HeroSection } from "./HeroSection";
import { InteractiveDemo } from "./InteractiveDemo";
import { FeatureGridSection } from "./FeatureGridSection";
import { ProductChromeShowcase } from "./ProductChromeShowcase";
import { ComparisonMatrix } from "./ComparisonMatrix";
import { WorkflowSteps } from "./WorkflowSteps";
import { CallToActionSection } from "./CallToActionSection";
import { LandingFooter } from "./LandingFooter";
import { QuickUploadModal } from "./QuickUploadModal";

export function LandingPageContainer() {
  return (
    <div className="relative min-h-screen bg-canvas text-ink flex flex-col font-sans selection:bg-primary/20 selection:text-ink">
      {/* Interactive Atmospheric Constellation & Perspective Grid Background */}
      <AtmosphericBackground />

      {/* Top Fixed Sticky Navigation */}
      <LandingNavbar />

      {/* Main Editorial Rhythm Bands */}
      <main className="flex-1 relative z-10">
        {/* Band 1: Literary Hero Section */}
        <HeroSection />

        {/* Band 2: Mac Studio Interactive Demo (Pixel-Perfect Anchored Bounding Box) */}
        <InteractiveDemo />

        {/* Band 3: 3 Streamlined Pillar Feature Cards */}
        <FeatureGridSection />

        {/* Band 4: Dark Navy Product Surfaces (Code & Sandbox Engine Showcase) */}
        <ProductChromeShowcase />

        {/* Band 5: Clean Academic Comparison Matrix */}
        <ComparisonMatrix />

        {/* Band 6: 4-Step Closed-Loop Workflow */}
        <WorkflowSteps />

        {/* Band 7: Full-Bleed Coral Pre-Footer Callout Band */}
        <CallToActionSection />
      </main>

      {/* Band 8: Dark Navy Closing Editorial Footer */}
      <LandingFooter />

      {/* Global Quick Upload Modal */}
      <QuickUploadModal />
    </div>
  );
}
