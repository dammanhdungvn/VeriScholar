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
});
