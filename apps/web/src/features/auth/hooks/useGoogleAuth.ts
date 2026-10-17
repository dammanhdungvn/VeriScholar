import * as React from "react";
import { useNavigate } from "react-router-dom";
import { authApi } from "../api/authApi";
import { useAuthStore } from "../stores/useAuthStore";

export interface UseGoogleAuthOptions {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useGoogleAuth(options: UseGoogleAuthOptions = {}) {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const clientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || "").trim();
  const isConfigured = Boolean(clientId && clientId.length > 0);

  const loginWithGoogleToken = React.useCallback(
    async (idToken: string) => {
      if (!idToken || !idToken.trim()) {
        const err = new Error("Mã Google ID Token không hợp lệ.");
        setError(err.message);
        options.onError?.(err);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const authResponse = await authApi.googleLogin(idToken.trim());
        login(authResponse, true);
        options.onSuccess?.();
        navigate("/dashboard");
      } catch (err: unknown) {
        const errorObj = err instanceof Error ? err : new Error("Đăng nhập Google thất bại.");
        setError(errorObj.message);
        options.onError?.(errorObj);
      } finally {
        setIsLoading(false);
      }
    },
    [login, navigate, options]
  );

  /**
   * Initializes Google Identity Services (GIS) on mount if GIS script & Client ID exist
   */
  const initializeGsi = React.useCallback(
    (onCredentialReceived?: (token: string) => void) => {
      if (typeof window === "undefined" || !window.google?.accounts?.id || !isConfigured) {
        return false;
      }

      try {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: (response: GoogleCredentialResponse) => {
            if (response.credential) {
              if (onCredentialReceived) {
                onCredentialReceived(response.credential);
              } else {
                void loginWithGoogleToken(response.credential);
              }
            }
          },
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        return true;
      } catch {
        return false;
      }
    },
    [clientId, isConfigured, loginWithGoogleToken]
  );

  /**
   * Triggers Google One Tap prompt if available
   */
  const promptGoogle = React.useCallback(() => {
    if (typeof window !== "undefined" && window.google?.accounts?.id && isConfigured) {
      window.google.accounts.id.prompt();
    }
  }, [isConfigured]);

  return {
    clientId,
    isConfigured,
    isLoading,
    error,
    loginWithGoogleToken,
    initializeGsi,
    promptGoogle,
    setError,
  };
}
