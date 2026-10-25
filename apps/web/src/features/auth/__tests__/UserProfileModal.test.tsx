import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { UserProfileModal, validateOrcidId, type UserProfileModalUser } from "@/components/profile/UserProfileModal";
import { authApi } from "@/features/auth/api/authApi";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";

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

  it("performs live E2E profile, theme, and BYOK update via UserProfileModal & authApi when backend is running", async () => {
    (globalThis as { __VITE_API_BASE_URL__?: string }).__VITE_API_BASE_URL__ =
      "http://localhost:8000";

    let backendReady = false;
    try {
      const probe = await fetch("http://localhost:8000/health/ready");
      backendReady = probe.ok;
    } catch {
      backendReady = false;
    }

    if (!backendReady) {
      return;
    }

    const uniqueEmail = `fe.scholar.${Date.now()}@vnu.edu.vn`;
    const regRes = await authApi.register({
      full_name: "PGS. TS. Trần Văn Khoa",
      email: uniqueEmail,
      password: "Password123!",
      accept_terms: true,
    });

    useAuthStore.getState().login(regRes, true);

    let latestUpdatedUser: UserProfileModalUser | null = null;
    render(
      <UserProfileModal
        isOpen={true}
        onClose={() => {}}
        user={regRes.user}
        onUpdated={(u) => {
          latestUpdatedUser = u;
        }}
      />
    );

    // 1. Tab 1: Set ORCID iD & Institution
    const orcidInput = screen.getByPlaceholderText("0000-0002-1825-0097");
    fireEvent.change(orcidInput, { target: { value: "0000-0002-1825-0097" } });
    fireEvent.click(screen.getByText(/Lưu hồ sơ/i));

    await waitFor(() => {
      expect(latestUpdatedUser?.orcid_id).toBe("0000-0002-1825-0097");
    });

    // 2. Tab 3: Switch Theme to Dark
    fireEvent.click(screen.getByText(/Giao diện/i));
    fireEvent.click(screen.getByText(/🌙 Tối/i));
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    // 3. Tab 2: Save & Verify BYOK Key
    fireEvent.click(screen.getByText(/Bảo mật & Khóa BYOK/i));
    const byokInput = screen.getByPlaceholderText("sk-proj-...");
    const testByokKey =
      (import.meta.env.VITE_TEST_BYOK_KEY as string | undefined) ||
      "sk-proj-verischolar-fe-e2e-9988";
    fireEvent.change(byokInput, { target: { value: testByokKey } });
    fireEvent.click(screen.getByText(/Lưu & Xác thực khóa/i));

    const expectedSuffix = testByokKey.trim().slice(-4);
    await waitFor(() => {
      expect(screen.getByTestId("byok-masked-badge")).toHaveTextContent(
        `sk-proj-...${expectedSuffix}`
      );
    });

    // 4. Verify via authApi.getMe() directly against live backend
    const meProfile = await authApi.getMe();
    expect(meProfile.has_byok).toBe(true);
    expect(meProfile.byok_masked).toBe(`sk-proj-...${expectedSuffix}`);
    expect(meProfile.orcid_id).toBe("0000-0002-1825-0097");
    expect(meProfile.theme_preference).toBe("dark");
  }, 30000);

  it("renders connected Google account card in Tab 2", () => {
    const mockUser = {
      id: "usr-123",
      email: "scholar@univ.edu.vn",
      full_name: "TS. Nguyễn Văn A",
      has_byok: true,
      byok_masked: "sk-proj-...4f8A",
      theme_preference: "dark" as const,
    };

    render(<UserProfileModal isOpen={true} onClose={() => {}} user={mockUser} />);
    fireEvent.click(screen.getByText(/Bảo mật & Khóa BYOK/i));
    expect(screen.getByText(/Tài khoản liên kết/i)).toBeInTheDocument();
    expect(screen.getByText(/Đã kết nối/i)).toBeInTheDocument();
  });

  it("displays error banner when profile update API fails", async () => {
    const mockUser = {
      id: "usr-123",
      email: "scholar@univ.edu.vn",
      full_name: "TS. Nguyễn Văn A",
      has_byok: false,
      byok_masked: null,
      theme_preference: "dark" as const,
    };

    const spy = vi.spyOn(authApi, "updateProfile").mockRejectedValueOnce(new Error("Network connection error"));

    render(<UserProfileModal isOpen={true} onClose={() => {}} user={mockUser} />);
    fireEvent.click(screen.getByText(/Lưu hồ sơ/i));

    await waitFor(() => {
      expect(screen.getByText(/Network connection error/i)).toBeInTheDocument();
    });

    spy.mockRestore();
  });
});
