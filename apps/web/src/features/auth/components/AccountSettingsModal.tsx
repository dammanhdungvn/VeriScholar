import { ScholarSettingsView } from "./ScholarSettingsView";

export interface AccountSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: "profile" | "connected" | "security";
}

export interface AccountSettingsContentProps {
  onClose?: () => void;
  defaultTab?: "profile" | "connected" | "security";
  isPage?: boolean;
}

export function AccountSettingsContent({
  onClose,
  defaultTab = "profile",
  isPage = false,
}: AccountSettingsContentProps) {
  const mappedTab = defaultTab === "connected" ? "security" : defaultTab;
  return (
    <ScholarSettingsView
      variant={isPage ? "page" : "dialog"}
      defaultTab={mappedTab}
      onClose={onClose}
    />
  );
}

export function AccountSettingsModal({
  isOpen,
  onClose,
  defaultTab = "profile",
}: AccountSettingsModalProps) {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Cài đặt tài khoản học giả"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <AccountSettingsContent onClose={onClose} defaultTab={defaultTab} isPage={false} />
    </div>
  );
}

export default AccountSettingsModal;
