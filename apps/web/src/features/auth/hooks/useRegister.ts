import { useMutation } from "@tanstack/react-query";
import type { RegisterPayload, AuthResponse } from "@/types/auth";
import { authApi } from "../api/authApi";
import { mockRegister } from "../data/mock-auth";
import { useAuthStore } from "../stores/useAuthStore";

export function useRegister() {
  const login = useAuthStore((s) => s.login);

  return useMutation<AuthResponse, Error, RegisterPayload>({
    mutationFn: async (payload: RegisterPayload) => {
      if (import.meta.env.VITE_ENABLE_MOCK_AUTH === "true") {
        return mockRegister(payload);
      }
      return authApi.register(payload);
    },
    onSuccess: (data) => {
      login(data, true);
    },
  });
}

