export interface PasswordStrength {
  score: number; // 0 to 4
  label: "Chưa nhập" | "Yếu" | "Trung bình" | "Khá" | "Rất mạnh";
  colorClass: string;
  hasMinLength: boolean;
  hasUppercase: boolean;
  hasNumber: boolean;
  hasSpecial: boolean;
  isAcceptable: boolean;
}

export function evaluatePasswordStrength(password: string): PasswordStrength {
  if (!password) {
    return {
      score: 0,
      label: "Chưa nhập",
      colorClass: "bg-hairline dark:bg-[#38332c]",
      hasMinLength: false,
      hasUppercase: false,
      hasNumber: false,
      hasSpecial: false,
      isAcceptable: false,
    };
  }

  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>_\-+=[\]\\]/.test(password);

  let score = 0;
  if (hasMinLength) score += 1;
  if (hasUppercase) score += 1;
  if (hasNumber) score += 1;
  if (hasSpecial) score += 1;

  let label: PasswordStrength["label"] = "Yếu";
  let colorClass = "bg-error";

  if (score === 2) {
    label = "Trung bình";
    colorClass = "bg-amber-500";
  } else if (score === 3) {
    label = "Khá";
    colorClass = "bg-accent-teal";
  } else if (score >= 4) {
    label = "Rất mạnh";
    colorClass = "bg-success";
  }

  return {
    score,
    label,
    colorClass,
    hasMinLength,
    hasUppercase,
    hasNumber,
    hasSpecial,
    isAcceptable: hasMinLength && score >= 2,
  };
}

export function isAcademicDomain(email: string): boolean {
  if (!email || !email.includes("@")) return false;
  const domain = email.split("@")[1]?.toLowerCase() || "";
  const academicSuffixes = [
    ".edu",
    ".edu.vn",
    ".ac.uk",
    ".ac.jp",
    ".org",
    ".ac.vn",
    "hcmut.edu.vn",
    "vnu.edu.vn",
    "verischolar.ai",
  ];
  return academicSuffixes.some((suffix) => domain.endsWith(suffix));
}
