import { useMutation } from "@tanstack/react-query";
import type { RegisterPayload, AuthResponse } from "@/types/auth";
import { authApi } from "../api/authApi";
import { useAuthStore } from "../stores/useAuthStore";

export function useRegister() {
  const login = useAuthStore((s) => s.login);

  return useMutation<AuthResponse, Error, RegisterPayload>({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
    onSuccess: (data) => {
      login(data, true);
    },
  });
}
