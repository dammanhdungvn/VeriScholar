import { useMutation } from "@tanstack/react-query";
import type { RegisterPayload, AuthResponse } from "@/types/auth";
import { mockRegister } from "../data/mock-auth";
import { useAuthStore } from "../stores/useAuthStore";

export function useRegister() {
  const login = useAuthStore((s) => s.login);

  return useMutation<AuthResponse, Error, RegisterPayload>({
    mutationFn: async (payload: RegisterPayload) => {
      return mockRegister(payload);
    },
    onSuccess: (data) => {
      login(data, true);
    },
  });
}
