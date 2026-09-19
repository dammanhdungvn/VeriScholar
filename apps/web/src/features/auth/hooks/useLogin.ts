import { useMutation } from "@tanstack/react-query";
import type { LoginCredentials, AuthResponse } from "@/types/auth";
import { mockLogin } from "../data/mock-auth";
import { useAuthStore } from "../stores/useAuthStore";

export function useLogin() {
  const login = useAuthStore((s) => s.login);

  return useMutation<AuthResponse, Error, LoginCredentials>({
    mutationFn: async (credentials: LoginCredentials) => {
      // In production, check import.meta.env.VITE_ENABLE_MOCK_AUTH === "true"
      return mockLogin(credentials);
    },
    onSuccess: (data, variables) => {
      login(data, variables.remember_me ?? true);
    },
  });
}
