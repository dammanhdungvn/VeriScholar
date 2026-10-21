import * as React from "react";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SocialAuthButtonsProps {
  onSocialAuth?: (provider: "google" | "github" | "orcid") => void;
  onGoogleSuccess?: (idToken: string) => void;
  onGoogleError?: (error: Error) => void;
  isLoading?: boolean;
  disabled?: boolean;
  className?: string;
}

export function SocialAuthButtons({
  onSocialAuth,
  onGoogleSuccess,
  isLoading = false,
  disabled = false,
  className,
}: SocialAuthButtonsProps) {
  const [activeProvider, setActiveProvider] = React.useState<"google" | "github" | "orcid" | null>(null);
  const googleBtnContainerRef = React.useRef<HTMLDivElement>(null);
  const clientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || "").trim();

  React.useEffect(() => {
    if (!clientId || !onGoogleSuccess || typeof window === "undefined") {
      return;
    }

    const initGsi = () => {
      if (window.google?.accounts?.id && googleBtnContainerRef.current) {
        try {
          window.google.accounts.id.initialize({
            client_id: clientId,
            callback: (response: GoogleCredentialResponse) => {
              if (response.credential) {
                setActiveProvider("google");
                onGoogleSuccess(response.credential);
              }
            },
            auto_select: false,
            cancel_on_tap_outside: true,
          });

          window.google.accounts.id.renderButton(googleBtnContainerRef.current, {
            type: "standard",
            theme: "outline",
            size: "large",
            width: 200,
          });
        } catch {
          // Ignore GIS initialization issues in restricted test environments
        }
      }
    };

    if (window.google?.accounts?.id) {
      initGsi();
    } else {
      const interval = setInterval(() => {
        if (window.google?.accounts?.id) {
          clearInterval(interval);
          initGsi();
        }
      }, 250);
      return () => clearInterval(interval);
    }
  }, [clientId, onGoogleSuccess]);

  const handleClick = (provider: "google" | "github" | "orcid") => {
    if (disabled || isLoading) return;
    setActiveProvider(provider);

    if (provider === "google" && clientId && window.google?.accounts?.id) {
      try {
        window.google.accounts.id.prompt();
      } catch {
        onSocialAuth?.(provider);
      }
      return;
    }

    onSocialAuth?.(provider);
  };

  return (
    <div className={cn("grid grid-cols-3 gap-2.5 w-full", className)}>
      {/* Google SSO Button - Icon only */}
      <div className="relative w-full">
        <Button
          type="button"
          variant="secondary"
          onClick={() => handleClick("google")}
          disabled={disabled || isLoading}
          aria-label="Google"
          title="Đăng nhập bằng Google"
          className="h-11 w-full flex items-center justify-center border-hairline dark:border-[#38332c] dark:bg-[#201e1b] dark:hover:bg-[#282522] transition-colors cursor-pointer rounded-xl relative overflow-hidden"
        >
          {isLoading && activeProvider === "google" ? (
            <Loader2 className="w-5 h-5 animate-spin text-muted" />
          ) : (
            <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
          )}
        </Button>
        {/* Invisible Google GSI native button overlay when configured */}
        {clientId && (
          <div
            ref={googleBtnContainerRef}
            className="absolute inset-0 opacity-0 cursor-pointer overflow-hidden flex items-center justify-center pointer-events-auto z-10"
            title="Đăng nhập với Google"
          />
        )}
      </div>

      {/* GitHub SSO Button - Icon only */}
      <Button
        type="button"
        variant="secondary"
        onClick={() => handleClick("github")}
        disabled={disabled || isLoading}
        aria-label="GitHub"
        title="Đăng nhập bằng GitHub"
        className="h-11 flex items-center justify-center border-hairline dark:border-[#38332c] dark:bg-[#201e1b] dark:hover:bg-[#282522] transition-colors cursor-pointer rounded-xl"
      >
        {isLoading && activeProvider === "github" ? (
          <Loader2 className="w-5 h-5 animate-spin text-muted" />
        ) : (
          <svg className="w-5 h-5 shrink-0 fill-current text-ink dark:text-zinc-100" viewBox="0 0 24 24">
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
            />
          </svg>
        )}
      </Button>

      {/* ORCID Academic SSO Button - Icon only */}
      <Button
        type="button"
        variant="secondary"
        onClick={() => handleClick("orcid")}
        disabled={disabled || isLoading}
        aria-label="ORCID"
        title="Đăng nhập bằng ORCID"
        className="h-11 flex items-center justify-center border-hairline dark:border-[#38332c] dark:bg-[#201e1b] dark:hover:bg-[#282522] transition-colors cursor-pointer rounded-xl"
      >
        {isLoading && activeProvider === "orcid" ? (
          <Loader2 className="w-5 h-5 animate-spin text-muted" />
        ) : (
          <svg className="w-5 h-5 shrink-0" viewBox="0 0 256 256" fill="none">
            <path
              d="M128 0C57.307 0 0 57.307 0 128s57.307 128 128 128 128-57.307 128-128S198.693 0 128 0z"
              fill="#A6CE39"
            />
            <path
              d="M86.3 186.2H70.9V79.1h15.4v107.1zm-7.7-123.6c-5.3 0-9.6-4.3-9.6-9.6s4.3-9.6 9.6-9.6 9.6 4.3 9.6 9.6c0 5.3-4.3 9.6-9.6 9.6zm35.2 123.6h38.2c26.9 0 43.1-18.4 43.1-43.5 0-25.1-16.2-43.5-43.1-43.5h-38.2v87zm15.4-72.9h21.4c17.5 0 27.6 11.8 27.6 29.4 0 17.6-10.1 29.4-27.6 29.4h-21.4v-58.8z"
              fill="#FFFFFF"
            />
          </svg>
        )}
      </Button>
    </div>
  );
}
