import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { AccountSettingsModal } from "./AccountSettingsModal";
import { useAuthStore } from "../stores/useAuthStore";
import { authApi } from "../api/authApi";
import type { UserProfile, AuthResponse } from "@/types/auth";

describe("AccountSettingsModal", () => {
  const mockUser: UserProfile = {
    id: "usr-456",
    email: "scholar.test@harvard.edu",
    full_name: "GS.TS. Tran Van Test",
    institution: "Harvard University",
    academic_rank: "Giáo sư",
    orcid_id: "0000-0001-2345-6789",
    role: "faculty",
    is_verified: true,
    created_at: "2026-01-01T00:00:00Z",
  };

  const mockAuthResponse: AuthResponse = {
    user: mockUser,
    tokens: {
      access_token: "test_access_token",
      refresh_token: "test_refresh_token",
      token_type: "bearer",
      expires_in: 3600,
    },
  };

  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().login(mockAuthResponse);
    vi.clearAllMocks();
  });

  it("does not render when isOpen is false", () => {
    render(<AccountSettingsModal isOpen={false} onClose={vi.fn()} />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders Profile tab by default with user information", () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} />);

    expect(screen.getByRole("dialog", { name: "Cài đặt tài khoản" })).toBeInTheDocument();
    expect(screen.getByText("scholar.test@harvard.edu")).toBeInTheDocument();
    expect(screen.getByLabelText(/Họ và tên/i)).toHaveValue("GS.TS. Tran Van Test");
    expect(screen.getByLabelText(/Cơ quan/i)).toHaveValue("Harvard University");
    expect(screen.getByLabelText(/Học hàm/i)).toHaveValue("Giáo sư");
    expect(screen.getByLabelText(/ORCID/i)).toHaveValue("0000-0001-2345-6789");
  });

  it("updates user profile on save and updates the store", async () => {
    vi.spyOn(authApi, "updateProfile").mockResolvedValueOnce({
      ...mockUser,
      full_name: "GS.TS. Tran Van Cap Nhat",
      institution: "MIT Media Lab",
    });

    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} />);

    const fullNameInput = screen.getByLabelText(/Họ và tên/i);
    const institutionInput = screen.getByLabelText(/Cơ quan/i);
    const saveButton = screen.getByRole("button", { name: /Lưu thay đổi/i });

    fireEvent.change(fullNameInput, { target: { value: "GS.TS. Tran Van Cap Nhat" } });
    fireEvent.change(institutionInput, { target: { value: "MIT Media Lab" } });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/Hồ sơ học giả đã được cập nhật thành công/i)).toBeInTheDocument();
    });

    const updatedUser = useAuthStore.getState().user;
    expect(updatedUser?.full_name).toBe("GS.TS. Tran Van Cap Nhat");
    expect(updatedUser?.institution).toBe("MIT Media Lab");
  });

  it("validates empty full name in profile form", async () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} />);

    const fullNameInput = screen.getByLabelText(/Họ và tên/i);
    const saveButton = screen.getByRole("button", { name: /Lưu thay đổi/i });

    fireEvent.change(fullNameInput, { target: { value: "   " } });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/Họ và tên không được để trống/i)).toBeInTheDocument();
    });
  });

  it("switches to Security tab and validates password mismatch", async () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} />);

    const securityTab = screen.getByRole("button", { name: /Bảo mật & Mật khẩu/i });
    fireEvent.click(securityTab);

    expect(screen.getByLabelText(/Mật khẩu hiện tại/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Mật khẩu mới/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Xác nhận mật khẩu mới/i)).toBeInTheDocument();

    const currentPwd = screen.getByLabelText(/Mật khẩu hiện tại/i);
    const newPwd = screen.getByLabelText(/^Mật khẩu mới/i);
    const confirmPwd = screen.getByLabelText(/Xác nhận mật khẩu mới/i);
    const submitBtn = screen.getByRole("button", { name: /Cập nhật mật khẩu/i });

    fireEvent.change(currentPwd, { target: { value: "OldPassword123!" } });
    fireEvent.change(newPwd, { target: { value: "NewPassword123!" } });
    fireEvent.change(confirmPwd, { target: { value: "DifferentPassword123!" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Mật khẩu xác nhận không khớp/i)).toBeInTheDocument();
    });
  });

  it("validates minimum 8 characters for new password", async () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} defaultTab="security" />);

    const currentPwd = screen.getByLabelText(/Mật khẩu hiện tại/i);
    const newPwd = screen.getByLabelText(/^Mật khẩu mới/i);
    const confirmPwd = screen.getByLabelText(/Xác nhận mật khẩu mới/i);
    const submitBtn = screen.getByRole("button", { name: /Cập nhật mật khẩu/i });

    fireEvent.change(currentPwd, { target: { value: "OldPassword123!" } });
    fireEvent.change(newPwd, { target: { value: "12345" } });
    fireEvent.change(confirmPwd, { target: { value: "12345" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/tối thiểu 8 ký tự/i)).toBeInTheDocument();
    });
  });

  it("submits password change successfully when inputs are valid", async () => {
    vi.spyOn(authApi, "changePassword").mockResolvedValueOnce({
      message: "Password changed successfully",
    });

    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} defaultTab="security" />);

    const currentPwd = screen.getByLabelText(/Mật khẩu hiện tại/i);
    const newPwd = screen.getByLabelText(/^Mật khẩu mới/i);
    const confirmPwd = screen.getByLabelText(/Xác nhận mật khẩu mới/i);
    const submitBtn = screen.getByRole("button", { name: /Cập nhật mật khẩu/i });

    fireEvent.change(currentPwd, { target: { value: "OldPassword123!" } });
    fireEvent.change(newPwd, { target: { value: "NewPassword123!" } });
    fireEvent.change(confirmPwd, { target: { value: "NewPassword123!" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/Mật khẩu đã được thay đổi thành công/i)).toBeInTheDocument();
    });
  });

  it("calls onClose when clicking close or cancel buttons", () => {
    const handleClose = vi.fn();
    render(<AccountSettingsModal isOpen={true} onClose={handleClose} />);

    const closeBtn = screen.getByRole("button", { name: "Đóng" });
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);

    const cancelBtn = screen.getByRole("button", { name: "Hủy" });
    fireEvent.click(cancelBtn);
    expect(handleClose).toHaveBeenCalledTimes(2);
  });

  it("renders Scholar Hero Card with large initials avatar, full name and verified trust badge", () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} />);

    // 1. Scholar Identity & Trust Badge
    expect(screen.getByText("GS.TS. Tran Van Test")).toBeInTheDocument();
    expect(screen.getByText(/Học giả đã xác thực \(ISO 32000-1 \/ DOI Ready\)/i)).toBeInTheDocument();
    expect(screen.getByText("faculty")).toBeInTheDocument();

    // 2. Initials Avatar
    expect(screen.getByText("GT")).toBeInTheDocument(); // GS.TS. ... Test -> GT
  });

  it("renders and updates new academic fields (department, google_scholar_url, research_interests, bio)", async () => {
    const updateSpy = vi.spyOn(authApi, "updateProfile").mockResolvedValueOnce({
      ...mockUser,
      department: "Khoa Khoa học & Kỹ thuật Máy tính",
      google_scholar_url: "https://scholar.google.com/citations?user=test1234",
      research_interests: "AI, NLP, Machine Learning",
      bio: "Giảng viên và nhà nghiên cứu chuyên sâu về mô hình ngôn ngữ lớn.",
    });

    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} />);

    const deptInput = screen.getByLabelText(/Khoa \/ Phòng thí nghiệm/i);
    const scholarInput = screen.getByLabelText(/Google Scholar Profile/i);
    const interestsInput = screen.getByLabelText(/Lĩnh vực nghiên cứu/i);
    const bioTextarea = screen.getByLabelText(/Tiểu sử học thuật/i);
    const saveButton = screen.getByRole("button", { name: /Lưu thay đổi/i });

    fireEvent.change(deptInput, { target: { value: "Khoa Khoa học & Kỹ thuật Máy tính" } });
    fireEvent.change(scholarInput, { target: { value: "https://scholar.google.com/citations?user=test1234" } });
    fireEvent.change(interestsInput, { target: { value: "AI, NLP, Machine Learning" } });
    fireEvent.change(bioTextarea, { target: { value: "Giảng viên và nhà nghiên cứu chuyên sâu về mô hình ngôn ngữ lớn." } });

    // Check tags preview
    expect(screen.getByText("#AI")).toBeInTheDocument();
    expect(screen.getByText("#NLP")).toBeInTheDocument();

    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          department: "Khoa Khoa học & Kỹ thuật Máy tính",
          google_scholar_url: "https://scholar.google.com/citations?user=test1234",
          research_interests: "AI, NLP, Machine Learning",
          bio: "Giảng viên và nhà nghiên cứu chuyên sâu về mô hình ngôn ngữ lớn.",
        })
      );
    });

    const updatedUser = useAuthStore.getState().user;
    expect(updatedUser?.department).toBe("Khoa Khoa học & Kỹ thuật Máy tính");
  });

  it("switches to Connected Accounts tab and displays Google GIS and ORCID status", () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} />);

    const connectedTab = screen.getByRole("button", { name: /Tài khoản liên kết/i });
    fireEvent.click(connectedTab);

    expect(screen.getByText("Google Workspace SSO")).toBeInTheDocument();
    expect(screen.getByText(/Đã kết nối qua Google GIS/i)).toBeInTheDocument();
    expect(screen.getByText("ORCID Member Registry")).toBeInTheDocument();
    expect(screen.getByText("Overleaf / LaTeX Cloud Workspace")).toBeInTheDocument();
  });

  it("switches to Security tab and renders active session card with logout button", () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} defaultTab="security" />);

    expect(screen.getByText(/Phiên làm việc hiện tại \(Active Session\)/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Đăng xuất thiết bị/i })).toBeInTheDocument();
  });

  it("validates current password is required when submitting password change", async () => {
    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} defaultTab="security" />);

    const newPwd = screen.getByLabelText(/^Mật khẩu mới/i);
    const confirmPwd = screen.getByLabelText(/Xác nhận mật khẩu mới/i);
    const submitBtn = screen.getByRole("button", { name: /Cập nhật mật khẩu/i });

    fireEvent.change(newPwd, { target: { value: "NewSecurePassword123!" } });
    fireEvent.change(confirmPwd, { target: { value: "NewSecurePassword123!" } });
    fireEvent.submit(submitBtn.closest("form")!);

    await waitFor(() => {
      expect(screen.getByText("Vui lòng nhập mật khẩu hiện tại.")).toBeInTheDocument();
    });
  });

  it("displays error alert when changePassword API fails (401/400/500)", async () => {
    vi.spyOn(authApi, "changePassword").mockRejectedValueOnce(
      new Error("Mật khẩu hiện tại không chính xác.")
    );

    render(<AccountSettingsModal isOpen={true} onClose={vi.fn()} defaultTab="security" />);

    const currentPwd = screen.getByLabelText(/Mật khẩu hiện tại/i);
    const newPwd = screen.getByLabelText(/^Mật khẩu mới/i);
    const confirmPwd = screen.getByLabelText(/Xác nhận mật khẩu mới/i);
    const submitBtn = screen.getByRole("button", { name: /Cập nhật mật khẩu/i });

    fireEvent.change(currentPwd, { target: { value: "WrongCurrentPassword123!" } });
    fireEvent.change(newPwd, { target: { value: "NewSecurePassword123!" } });
    fireEvent.change(confirmPwd, { target: { value: "NewSecurePassword123!" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Mật khẩu hiện tại không chính xác.")).toBeInTheDocument();
    });
  });
});
