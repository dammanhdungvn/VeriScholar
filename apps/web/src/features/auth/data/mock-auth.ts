import type {
  LoginCredentials,
  RegisterPayload,
  AuthResponse,
  UserProfile,
  AuthTokens,
} from "@/types/auth";
import { MOCK_USERS, type MockUserAccount } from "./mock-users";

// In-memory dynamic list for newly registered users during dev session
const dynamicUsers: MockUserAccount[] = [...MOCK_USERS];

function createMockTokens(): AuthTokens {
  const randomSuffix = Math.random().toString(36).substring(2);
  return {
    access_token: `mock_vs_at_${Date.now()}_${randomSuffix}`,
    refresh_token: `mock_vs_rt_${Date.now()}_${randomSuffix}`,
    token_type: "bearer",
    expires_in: 3600,
  };
}

export async function mockLogin(credentials: LoginCredentials): Promise<AuthResponse> {
  // Simulate network latency (400ms - 600ms)
  await new Promise((resolve) => setTimeout(resolve, 500));

  if (credentials.email === "timeout@error.com") {
    throw new Error("Không thể kết nối đến máy chủ xác thực. Vui lòng kiểm tra lại kết nối mạng.");
  }

  const normalizedEmail = credentials.email.trim().toLowerCase();
  const account = dynamicUsers.find((acc) => acc.user.email.toLowerCase() === normalizedEmail);

  if (!account) {
    throw new Error("Tài khoản không tồn tại. Vui lòng kiểm tra lại email hoặc đăng ký tài khoản mới.");
  }

  const isDemoScholar = account.user.email.toLowerCase() === "scholar@verischolar.ai";
  const isPasswordValid =
    account.passwordHash === credentials.password ||
    (isDemoScholar && (credentials.password === "VeriScholar2026!" || credentials.password === "VeriScholar@2026"));

  if (!isPasswordValid) {
    throw new Error("Mật khẩu không chính xác. Vui lòng thử lại hoặc chọn 'Quên mật khẩu'.");
  }

  return {
    user: { ...account.user },
    tokens: createMockTokens(),
    message: "Đăng nhập thành công vào VeriScholar.",
  };
}

export async function mockRegister(payload: RegisterPayload): Promise<AuthResponse> {
  await new Promise((resolve) => setTimeout(resolve, 600));

  const normalizedEmail = payload.email.trim().toLowerCase();
  const existing = dynamicUsers.find((acc) => acc.user.email.toLowerCase() === normalizedEmail);

  if (existing) {
    throw new Error("Email học thuật này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác.");
  }

  const newUser: UserProfile = {
    id: `usr-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 9)}`,
    email: payload.email.trim(),
    full_name: payload.full_name.trim(),
    institution: payload.institution?.trim() || "Viện Nghiên cứu Độc lập",
    academic_rank: "Nhà nghiên cứu Khoa học",
    orcid_id: payload.orcid_id?.trim() || undefined,
    role: "researcher",
    is_verified: true,
    created_at: new Date().toISOString(),
  };

  dynamicUsers.push({
    user: newUser,
    passwordHash: payload.password,
  });

  return {
    user: newUser,
    tokens: createMockTokens(),
    message: "Đăng ký thành viên nghiên cứu thành công! Chào mừng bạn đến với VeriScholar.",
  };
}

export async function mockForgotPassword(email: string): Promise<{ success: boolean; message: string }> {
  await new Promise((resolve) => setTimeout(resolve, 450));

  if (!email || !email.includes("@")) {
    throw new Error("Vui lòng nhập địa chỉ email hợp lệ.");
  }

  return {
    success: true,
    message: `Liên kết thiết lập lại mật khẩu bảo mật đã được gửi tới ${email}. Vui lòng kiểm tra hộp thư đến.`,
  };
}

export async function mockSocialAuth(provider: "google" | "orcid"): Promise<AuthResponse> {
  await new Promise((resolve) => setTimeout(resolve, 600));

  const providerNames = {
    google: "Google Scholar Academic",
    orcid: "ORCID Global Researcher",
  };

  const socialUser: UserProfile = {
    id: `usr-sso-${provider}-${Date.now().toString(36)}`,
    email: provider === "orcid" ? "researcher@orcid.org" : "scholar.google@gmail.com",
    full_name: provider === "orcid" ? "ORCID Verified Scholar" : "Google Scholar User",
    institution: "International Research Consortium",
    academic_rank: "Đồng tác giả Quốc tế",
    orcid_id: provider === "orcid" ? "0000-0002-1825-0097" : undefined,
    role: "researcher",
    is_verified: true,
    created_at: new Date().toISOString(),
  };

  return {
    user: socialUser,
    tokens: createMockTokens(),
    message: `Đăng nhập thành công qua ${providerNames[provider]}.`,
  };
}
