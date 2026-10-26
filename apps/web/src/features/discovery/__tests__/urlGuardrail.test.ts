import { describe, it, expect } from "vitest";
import {
  parseScholarlyInput,
  UNTRUSTED_URL_MESSAGE,
} from "../lib/urlGuardrail";

describe("urlGuardrail - parseScholarlyInput", () => {
  describe("arXiv URL parsing", () => {
    it("parses standard arXiv abstract URL", () => {
      const result = parseScholarlyInput("https://arxiv.org/abs/2305.18290");
      expect(result).toEqual({
        type: "scholarly_url",
        idType: "arxiv",
        identifier: "2305.18290",
      });
    });

    it("parses arXiv PDF URL with version and .pdf suffix", () => {
      const result = parseScholarlyInput(
        "https://arxiv.org/pdf/2404.10981v2.pdf"
      );
      expect(result).toEqual({
        type: "scholarly_url",
        idType: "arxiv",
        identifier: "2404.10981v2",
      });
    });

    it("parses arXiv URL without protocol prefix", () => {
      const result = parseScholarlyInput("arxiv.org/abs/2305.18290");
      expect(result).toEqual({
        type: "scholarly_url",
        idType: "arxiv",
        identifier: "2305.18290",
      });
    });

    it("parses arXiv URL with query parameters and fragments", () => {
      const result = parseScholarlyInput(
        "https://arxiv.org/abs/2305.18290?context=cs.AI#main"
      );
      expect(result).toEqual({
        type: "scholarly_url",
        idType: "arxiv",
        identifier: "2305.18290",
      });
    });
  });

  describe("DOI URL parsing", () => {
    it("parses standard DOI URL from doi.org", () => {
      const result = parseScholarlyInput("https://doi.org/10.1145/3805774");
      expect(result).toEqual({
        type: "scholarly_url",
        idType: "doi",
        identifier: "10.1145/3805774",
      });
    });

    it("parses DOI URL from whitelisted publisher domain (acm.org)", () => {
      const result = parseScholarlyInput(
        "https://dl.acm.org/doi/10.1145/3805774"
      );
      expect(result).toEqual({
        type: "scholarly_url",
        idType: "doi",
        identifier: "10.1145/3805774",
      });
    });
  });

  describe("Untrusted & malicious URL detection", () => {
    it("rejects adult or untrusted video domains", () => {
      const result = parseScholarlyInput("https://pornhub.com/video");
      expect(result).toEqual({
        type: "invalid_url",
        message: UNTRUSTED_URL_MESSAGE,
      });
    });

    it("rejects suspicious / phishing domains", () => {
      const result = parseScholarlyInput("https://phishing.xyz");
      expect(result).toEqual({
        type: "invalid_url",
        message: UNTRUSTED_URL_MESSAGE,
      });
    });

    it("rejects domain spoofing attempts (e.g. attacker domain with arxiv subdomain)", () => {
      const result = parseScholarlyInput("https://arxiv.org.attacker.com/abs/1234");
      expect(result).toEqual({
        type: "invalid_url",
        message: UNTRUSTED_URL_MESSAGE,
      });
    });

    it("rejects generic arbitrary websites", () => {
      const result = parseScholarlyInput("https://example.com/test");
      expect(result).toEqual({
        type: "invalid_url",
        message: UNTRUSTED_URL_MESSAGE,
      });
    });
  });

  describe("Regular search keywords", () => {
    it("treats academic paper title as keyword query", () => {
      const result = parseScholarlyInput("Attention Is All You Need");
      expect(result).toEqual({
        type: "keyword",
        query: "Attention Is All You Need",
      });
    });

    it("treats single topic keyword as keyword query", () => {
      const result = parseScholarlyInput("Transformer");
      expect(result).toEqual({
        type: "keyword",
        query: "Transformer",
      });
    });

    it("trims whitespace from keyword query", () => {
      const result = parseScholarlyInput("  Direct Preference Optimization  ");
      expect(result).toEqual({
        type: "keyword",
        query: "Direct Preference Optimization",
      });
    });
  });
});
