import React from "react";
import {
  ScholarSettingsView,
  validateOrcidId,
  maskClientApiKey,
  ORCID_REGEX,
  type ScholarUser,
} from "@/features/auth/components/ScholarSettingsView";

export { validateOrcidId, maskClientApiKey, ORCID_REGEX };

export type UserProfileModalUser = ScholarUser;

export interface UserProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: UserProfileModalUser | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onUpdated?: (updatedUser: any) => void;
}

export function UserProfileModal({
  isOpen,
  onClose,
  user,
  onUpdated,
}: UserProfileModalProps) {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Thiết lập tài khoản học giả"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <ScholarSettingsView
        variant="dialog"
        onClose={onClose}
        user={user}
        onUpdated={onUpdated}
      />
    </div>
  );
}

export default UserProfileModal;
