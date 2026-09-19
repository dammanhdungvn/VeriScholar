import { Menu, X, ArrowUpRight, Sparkles } from "lucide-react";
import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { Button } from "@/components/ui/button";
import { useLandingStore } from "../stores/useLandingStore";

export function LandingNavbar() {
  const isMobileMenuOpen = useLandingStore((s) => s.isMobileMenuOpen);
  const setMobileMenuOpen = useLandingStore((s) => s.setMobileMenuOpen);
  const setUploadModalOpen = useLandingStore((s) => s.setUploadModalOpen);

  const navLinks = [
    { label: "Tính năng", href: "#features" },
    { label: "Trình diễn", href: "#interactive-demo" },
    { label: "Đối sánh", href: "#comparison" },
    { label: "Quy trình", href: "#workflow" },
  ];

  return (
    <header className="sticky top-0 z-40 w-full h-16 bg-[#faf9f5]/85 backdrop-blur-md border-b border-hairline/80 transition-all">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between">
        {/* Logo */}
        <a href="#" className="flex items-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm">
          <AcademicLogo size="md" />
        </a>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-7" aria-label="Điều hướng chính">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-xs font-sans font-medium text-muted hover:text-ink transition-colors cursor-pointer"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Right CTA Cluster */}
        <div className="hidden sm:flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setUploadModalOpen(true)}
            className="text-xs text-muted hover:text-ink cursor-pointer"
          >
            Đăng nhập
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => setUploadModalOpen(true)}
            data-testid="nav-try-btn"
            className="group text-xs cursor-pointer shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5 text-on-primary transition-transform group-hover:scale-110" />
            <span>Dùng thử ngay</span>
            <ArrowUpRight className="w-3 h-3 text-on-primary/80 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </Button>
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex md:hidden items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={() => setUploadModalOpen(true)}
            className="text-xs px-3"
          >
            Dùng thử
          </Button>
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-ink rounded-md hover:bg-surface-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-primary cursor-pointer"
            aria-expanded={isMobileMenuOpen}
            aria-label="Mở danh mục điều hướng"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Sheet */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-b border-hairline bg-[#faf9f5] px-4 pt-2 pb-6 space-y-3 shadow-md animate-in fade-in slide-in-from-top-2">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block py-2 text-sm font-sans font-medium text-ink hover:text-primary transition-colors"
            >
              {link.label}
            </a>
          ))}
          <div className="pt-3 border-t border-hairline flex flex-col gap-2">
            <Button
              variant="secondary"
              size="md"
              className="w-full justify-center text-xs"
              onClick={() => {
                setMobileMenuOpen(false);
                setUploadModalOpen(true);
              }}
            >
              Đăng nhập
            </Button>
            <Button
              variant="primary"
              size="md"
              className="w-full justify-center text-xs"
              onClick={() => {
                setMobileMenuOpen(false);
                setUploadModalOpen(true);
              }}
            >
              Bắt đầu Nghiên cứu — Miễn phí
            </Button>
          </div>
        </div>
      )}
    </header>
  );
}
