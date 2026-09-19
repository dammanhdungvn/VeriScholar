import { AcademicLogo } from "@/components/shared/AcademicLogo";
import { useAuthStore } from "@/features/auth/stores/useAuthStore";
import { useTheme } from "@/hooks/useTheme";
import { DashboardChatInputBox } from "./DashboardChatInputBox";

interface DashboardHeroSectionProps {
  inputText: string;
  onChangeText: (text: string) => void;
  onSend: (text?: string) => void;
  isGenerating?: boolean;
  onUploadFile?: (file: File) => void;
}

export function DashboardHeroSection({
  inputText,
  onChangeText,
  onSend,
  isGenerating = false,
  onUploadFile
}: DashboardHeroSectionProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const { user } = useAuthStore();

  const userGreetingName = user?.full_name
    ? user.full_name.split(" ").slice(-2).join(" ")
    : "Nhà nghiên cứu";

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 py-8 select-text overflow-y-auto w-full custom-scrollbar">
      {/* 1. Academic Header */}
      <div className="flex flex-col items-center text-center mb-6 select-none">
        <div className="flex items-center gap-3 justify-center">
          <div className="w-10 h-10 rounded-2xl bg-white dark:bg-[#24221f] border border-[#e5dfd4] dark:border-[#38332c] p-2 shadow-xs flex items-center justify-center">
            <AcademicLogo size="sm" inverted={isDark} showWordmark={false} />
          </div>
          <h1 className="font-sans text-2xl sm:text-3xl md:text-4xl tracking-tight text-ink dark:text-[#f7f5ef] font-semibold">
            Không gian nghiên cứu, {userGreetingName}
          </h1>
        </div>
      </div>

      {/* 2. Center Floating Input Box */}
      <DashboardChatInputBox
        inputText={inputText}
        onChangeText={onChangeText}
        onSend={onSend}
        isGenerating={isGenerating}
        onUploadFile={onUploadFile}
      />
    </div>
  );
}
