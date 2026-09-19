import { AcademicLogo } from "@/components/shared/AcademicLogo";

export function LandingFooter() {
  const footerLinks = {
    product: [
      { label: "Đọc sâu & Bounding Box", href: "#interactive-demo" },
      { label: "Trợ lý Socratic Mentor", href: "#features" },
      { label: "Kiểm chứng SAFE Fact-Checking", href: "#features" },
      { label: "Sandbox TeXLive Tự Vá Lỗi", href: "#features" },
      { label: "Xuất Gói Ngoại Tuyến ISO 32000-1", href: "#features" },
    ],
    academic: [
      { label: "Kho Tích Hợp arXiv", href: "#" },
      { label: "Cơ Sở Dữ Liệu PubMed", href: "#" },
      { label: "Đồ Thị Trích Dẫn 2-Hop", href: "#" },
      { label: "Chuẩn Hóa BibTeX & LaTeX", href: "#" },
      { label: "Bộ Tiêu Chuẩn NLI SAFE", href: "#" },
    ],
    resources: [
      { label: "Tài liệu Kiến trúc Hệ thống", href: "#" },
      { label: "Đặc tả API REST & SSE", href: "#" },
      { label: "Hướng dẫn Trích dẫn Khoa học", href: "#" },
      { label: "Bộ Thử Nghiệm Benchmark", href: "#comparison" },
      { label: "Mã nguồn Mở GitHub", href: "https://github.com/dammanhdungvn/VeriScholar" },
    ],
    privacy: [
      { label: "Chính sách Quyền Riêng Tư", href: "#security" },
      { label: "Cam kết Zero Data Retention", href: "#security" },
      { label: "Quy trình Xóa Tệp Chuẩn CAS", href: "#security" },
      { label: "Điều khoản Sử dụng Nghiên cứu", href: "#" },
      { label: "Bảo Mật Cơ Sở Dữ Liệu", href: "#" },
    ],
  };

  return (
    <footer id="security" className="bg-surface-dark text-on-dark-soft pt-16 pb-12 border-t border-[#2e2c28]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Top Brand Bar */}
        <div className="pb-10 border-b border-[#2e2c28] flex items-center justify-between">
          <div className="flex flex-col gap-2">
            <AcademicLogo size="lg" inverted showWordmark />
          </div>
        </div>

        {/* 4-Column Links Grid */}
        <div className="py-12 grid grid-cols-2 md:grid-cols-4 gap-8 text-xs font-sans">
          {/* Column 1 */}
          <div>
            <h4 className="font-sans font-semibold text-on-dark uppercase tracking-wider mb-4">
              Sản Phẩm & Tính Năng
            </h4>
            <ul className="space-y-2.5">
              {footerLinks.product.map((l, i) => (
                <li key={i}>
                  <a href={l.href} className="hover:text-on-dark transition-colors">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 2 */}
          <div>
            <h4 className="font-sans font-semibold text-on-dark uppercase tracking-wider mb-4">
              Học Thuật & Dữ Liệu
            </h4>
            <ul className="space-y-2.5">
              {footerLinks.academic.map((l, i) => (
                <li key={i}>
                  <a href={l.href} className="hover:text-on-dark transition-colors">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 3 */}
          <div>
            <h4 className="font-sans font-semibold text-on-dark uppercase tracking-wider mb-4">
              Tài Nguyên Kỹ Thuật
            </h4>
            <ul className="space-y-2.5">
              {footerLinks.resources.map((l, i) => (
                <li key={i}>
                  <a href={l.href} className="hover:text-on-dark transition-colors">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Column 4 */}
          <div>
            <h4 className="font-sans font-semibold text-on-dark uppercase tracking-wider mb-4">
              Bảo Mật & Pháp Lý
            </h4>
            <ul className="space-y-2.5">
              {footerLinks.privacy.map((l, i) => (
                <li key={i}>
                  <a href={l.href} className="hover:text-on-dark transition-colors">
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </footer>
  );
}
