import { useMutation } from "@tanstack/react-query";
import type { LoginCredentials, AuthResponse } from "@/types/auth";
import { authApi } from "../api/authApi";
import { mockLogin } from "../data/mock-auth";
import { useAuthStore } from "../stores/useAuthStore";

export function useLogin() {
  const login = useAuthStore((s) => s.login);

  return useMutation<AuthResponse, Error, LoginCredentials>({
    mutationFn: async (credentials: LoginCredentials) => {
      if (import.meta.env.VITE_ENABLE_MOCK_AUTH === "true") {
        return mockLogin(credentials);
      }
      return authApi.login(credentials);
    },
    onSuccess: (data, variables) => {
      login(data, variables.remember_me ?? true);
    },
  });
}

