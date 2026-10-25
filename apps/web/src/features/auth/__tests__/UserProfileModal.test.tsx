import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { UserProfileModal, validateOrcidId } from "@/components/profile/UserProfileModal";

describe("UserProfileModal 3 Tabs Component", () => {
  it("renders 3 tabs and displays masked BYOK key when available", () => {
    const mockUser = {
      id: "usr-123",
      email: "scholar@univ.edu.vn",
      full_name: "TS. Nguyễn Văn A",
      has_byok: true,
      byok_masked: "sk-proj-...4f8A",
      theme_preference: "dark" as const,
      orcid_id: "0000-0002-1825-0097",
    };

    render(<UserProfileModal isOpen={true} onClose={() => {}} user={mockUser} />);

    expect(screen.getByText(/Hồ sơ Học thuật/i)).toBeInTheDocument();
    expect(screen.getByText(/Bảo mật & Khóa BYOK/i)).toBeInTheDocument();
    expect(screen.getByText(/Giao diện/i)).toBeInTheDocument();

    // Click Tab 2
    fireEvent.click(screen.getByText(/Bảo mật & Khóa BYOK/i));
    expect(screen.getByText(/sk-proj-...4f8A/i)).toBeInTheDocument();
  });

  it("validates ORCID format and synchronizes dark theme on documentElement", () => {
    expect(validateOrcidId("0000-0002-1825-0097")).toBe(true);
    expect(validateOrcidId("0000-0001-5109-370X")).toBe(true);
    expect(validateOrcidId("invalid-orcid")).toBe(false);

    const mockUser = {
      id: "usr-123",
      email: "scholar@univ.edu.vn",
      full_name: "TS. Nguyễn Văn A",
      has_byok: false,
      byok_masked: null,
      theme_preference: "light" as const,
    };

    render(<UserProfileModal isOpen={true} onClose={() => {}} user={mockUser} />);

    // Switch to Tab 3: Giao diện
    fireEvent.click(screen.getByText(/Giao diện/i));
    fireEvent.click(screen.getByText(/🌙 Tối/i));
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    fireEvent.click(screen.getByText(/☀️ Sáng/i));
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
