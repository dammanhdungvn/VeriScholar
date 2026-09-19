import type { UserProfile } from "@/types/auth";

export interface MockUserAccount {
  user: UserProfile;
  passwordHash: string; // Plain password for mock verification
}

export const MOCK_USERS: MockUserAccount[] = [
  {
    user: {
      id: "usr-00000001-a1b2-c3d4-e5f6-789012345678",
      email: "scholar@verischolar.ai",
      full_name: "GS.TS. Nguyễn Văn Scholar",
      institution: "Viện Hàn lâm Khoa học & Công nghệ",
      academic_rank: "Giáo sư, Tiến sĩ Khoa học",
      orcid_id: "0000-0002-1825-0097",
      role: "faculty",
      is_verified: true,
      created_at: "2026-01-15T08:00:00Z",
    },
    passwordHash: "VeriScholar2026!",
  },
  {
    user: {
      id: "usr-00000002-b2c3-d4e5-f6a7-890123456789",
      email: "researcher@stanford.edu",
      full_name: "Dr. Elena Rostova",
      institution: "Stanford Artificial Intelligence Laboratory",
      academic_rank: "Senior Postdoctoral Fellow",
      orcid_id: "0000-0003-4567-8901",
      role: "researcher",
      is_verified: true,
      created_at: "2026-02-01T10:30:00Z",
    },
    passwordHash: "AcademicResearch#1",
  },
  {
    user: {
      id: "usr-00000003-c3d4-e5f6-a7b8-901234567890",
      email: "dung.dm@hcmut.edu.vn",
      full_name: "Đàm Mạnh Dũng",
      institution: "Đại học Bách Khoa TP.HCM (HCMUT)",
      academic_rank: "Nghiên cứu sinh AI",
      orcid_id: "0000-0001-9876-5432",
      role: "researcher",
      is_verified: true,
      created_at: "2026-03-01T14:15:00Z",
    },
    passwordHash: "BachKhoa2026!",
  },
];
