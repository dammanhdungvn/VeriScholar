import { describe, it, expect } from "vitest";
import {
  validateEmail,
  validateFullName,
  isValidEmailSyntax,
  isDisposableDomain,
  isAcademicEmail,
} from "./emailValidation";

describe("emailValidation utility", () => {
  describe("isValidEmailSyntax", () => {
    it("validates RFC compliant email addresses", () => {
      expect(isValidEmailSyntax("scholar@university.edu")).toBe(true);
      expect(isValidEmailSyntax("researcher.ai@hcmut.edu.vn")).toBe(true);
      expect(isValidEmailSyntax("dr_smith+lab@oxford.ac.uk")).toBe(true);
    });

    it("rejects invalid emails", () => {
      expect(isValidEmailSyntax("")).toBe(false);
      expect(isValidEmailSyntax("invalid-email")).toBe(false);
      expect(isValidEmailSyntax("@nodomain.com")).toBe(false);
      expect(isValidEmailSyntax("user@")).toBe(false);
      expect(isValidEmailSyntax("user@domain..com")).toBe(false);
      expect(isValidEmailSyntax("user@-domain.com")).toBe(false);
    });
  });

  describe("isDisposableDomain", () => {
    it("detects disposable email providers", () => {
      expect(isDisposableDomain("mailinator.com")).toBe(true);
      expect(isDisposableDomain("user@tempmail.com")).toBe(true);
      expect(isDisposableDomain("10minutemail.com")).toBe(true);
      expect(isDisposableDomain("guerrillamail.com")).toBe(true);
      expect(isDisposableDomain("user@gmail.com")).toBe(false);
      expect(isDisposableDomain("user@mit.edu")).toBe(false);
    });
  });

  describe("isAcademicEmail", () => {
    it("recognizes trusted academic suffixes", () => {
      expect(isAcademicEmail("phd@harvard.edu")).toBe(true);
      expect(isAcademicEmail("prof@vnu.edu.vn")).toBe(true);
      expect(isAcademicEmail("postdoc@cambridge.ac.uk")).toBe(true);
      expect(isAcademicEmail("fellow@u-tokyo.ac.jp")).toBe(true);
      expect(isAcademicEmail("regular@gmail.com")).toBe(false);
    });
  });

  describe("validateEmail (Tier-1 validation)", () => {
    it("rejects empty or whitespace emails", () => {
      const res = validateEmail("   ");
      expect(res.isValid).toBe(false);
      expect(res.error).toContain("Vui lòng nhập địa chỉ email");
    });

    it("blocks disposable email addresses with clear message", () => {
      const res = validateEmail("scammer@mailinator.com");
      expect(res.isValid).toBe(false);
      expect(res.isDisposable).toBe(true);
      expect(res.error).toContain("dịch vụ email tạm thời");
    });

    it("accepts academic emails and marks them as isAcademic", () => {
      const res = validateEmail("researcher@stanford.edu");
      expect(res.isValid).toBe(true);
      expect(res.isAcademic).toBe(true);
      expect(res.isDisposable).toBe(false);
      expect(res.error).toBeUndefined();
    });

    it("accepts reputable major providers (Gmail, Outlook, etc.)", () => {
      const res = validateEmail("author@gmail.com");
      expect(res.isValid).toBe(true);
      expect(res.isAcademic).toBe(false);
      expect(res.isDisposable).toBe(false);

      expect(validateEmail("user@outlook.com").isValid).toBe(true);
      expect(validateEmail("user@hotmail.com").isValid).toBe(true);
      expect(validateEmail("user@icloud.com").isValid).toBe(true);
      expect(validateEmail("user@proton.me").isValid).toBe(true);
      expect(validateEmail("admin@nih.gov").isValid).toBe(true);
      expect(validateEmail("editor@acm.org").isValid).toBe(true);
    });

    it("strictly blocks unwhitelisted commercial domains like maxxspace.com", () => {
      const res = validateEmail("user@maxxspace.com");
      expect(res.isValid).toBe(false);
      expect(res.isDisposable).toBe(false);
      expect(res.error).toContain("không thuộc danh mục được phép");
    });
  });

  describe("validateFullName", () => {
    it("accepts valid full names with at least 2 words", () => {
      expect(validateFullName("Nguyễn Văn A").isValid).toBe(true);
      expect(validateFullName("Marie Curie").isValid).toBe(true);
      expect(validateFullName("Trần Lê Minh").isValid).toBe(true);
    });

    it("rejects single-word names", () => {
      const res = validateFullName("John");
      expect(res.isValid).toBe(false);
      expect(res.error).toContain("tối thiểu 2 từ");
    });

    it("rejects names with special injection characters", () => {
      const res = validateFullName("<script>alert(1)</script>");
      expect(res.isValid).toBe(false);
      expect(res.error).toContain("ký tự đặc biệt không hợp lệ");
    });

    it("rejects empty names or names that are too short", () => {
      expect(validateFullName("").isValid).toBe(false);
      expect(validateFullName("A").isValid).toBe(false);
    });
  });
});
