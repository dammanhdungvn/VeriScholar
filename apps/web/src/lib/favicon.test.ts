import { describe, it, expect, beforeEach, vi } from "vitest";
import { updateFavicon, initFaviconSwitcher, isBrowserDarkMode } from "./favicon";

describe("favicon switcher", () => {
  beforeEach(() => {
    document.head.innerHTML = "";
  });

  it("applies dark mode favicons (light mark for dark tabs)", () => {
    updateFavicon(true, document);

    const svgLink = document.getElementById("favicon-svg") as HTMLLinkElement | null;
    const png32Link = document.getElementById("favicon-32") as HTMLLinkElement | null;
    const png16Link = document.getElementById("favicon-16") as HTMLLinkElement | null;
    const icoLink = document.getElementById("favicon-ico") as HTMLLinkElement | null;

    expect(svgLink).not.toBeNull();
    expect(svgLink?.getAttribute("href")).toBe("/favicon-dark.svg?v=dark");
    expect(svgLink?.getAttribute("type")).toBe("image/svg+xml");

    expect(png32Link).not.toBeNull();
    expect(png32Link?.getAttribute("href")).toBe("/favicon-dark-32x32.png?v=dark");
    expect(png32Link?.getAttribute("sizes")).toBe("32x32");

    expect(png16Link).not.toBeNull();
    expect(png16Link?.getAttribute("href")).toBe("/favicon-dark-16x16.png?v=dark");

    expect(icoLink).not.toBeNull();
    expect(icoLink?.getAttribute("href")).toBe("/favicon-dark.ico?v=dark");
  });

  it("applies light mode favicons (dark mark for light tabs)", () => {
    updateFavicon(false, document);

    const svgLink = document.getElementById("favicon-svg") as HTMLLinkElement | null;
    const png32Link = document.getElementById("favicon-32") as HTMLLinkElement | null;
    const png16Link = document.getElementById("favicon-16") as HTMLLinkElement | null;
    const icoLink = document.getElementById("favicon-ico") as HTMLLinkElement | null;

    expect(svgLink?.getAttribute("href")).toBe("/favicon-light.svg?v=light");
    expect(png32Link?.getAttribute("href")).toBe("/favicon-light-32x32.png?v=light");
    expect(png16Link?.getAttribute("href")).toBe("/favicon-light-16x16.png?v=light");
    expect(icoLink?.getAttribute("href")).toBe("/favicon-light.ico?v=light");
  });

  it("replaces existing links cleanly when mode changes", () => {
    // Start in light mode
    updateFavicon(false, document);
    expect((document.getElementById("favicon-svg") as HTMLLinkElement).getAttribute("href")).toBe("/favicon-light.svg?v=light");

    // Switch to dark mode
    updateFavicon(true, document);
    expect((document.getElementById("favicon-svg") as HTMLLinkElement).getAttribute("href")).toBe("/favicon-dark.svg?v=dark");

    // Ensure no duplicate link elements exist
    const svgLinks = document.querySelectorAll('link[id="favicon-svg"]');
    expect(svgLinks.length).toBe(1);
  });

  it("initializes matcher and responds to system change events", () => {
    let changeHandler: ((e: { matches: boolean }) => void) | null = null;

    const mockMatchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: true,
      media: query,
      addEventListener: vi.fn((event: string, handler: (e: { matches: boolean }) => void) => {
        if (event === "change") changeHandler = handler;
      }),
      removeEventListener: vi.fn(),
    }));

    const mockWindow = {
      matchMedia: mockMatchMedia,
      document,
    } as unknown as Window;

    const cleanup = initFaviconSwitcher(mockWindow);

    expect(mockMatchMedia).toHaveBeenCalledWith("(prefers-color-scheme: dark)");
    expect((document.getElementById("favicon-svg") as HTMLLinkElement).getAttribute("href")).toBe("/favicon-dark.svg?v=dark");

    // Simulate system changing to light mode
    if (changeHandler) {
      (changeHandler as (e: { matches: boolean }) => void)({ matches: false });
    }
    expect((document.getElementById("favicon-svg") as HTMLLinkElement).getAttribute("href")).toBe("/favicon-light.svg?v=light");

    cleanup();
  });

  it("checks browser dark mode correctly", () => {
    const mockWindowDark = {
      matchMedia: vi.fn().mockReturnValue({ matches: true }),
    } as unknown as Window;
    expect(isBrowserDarkMode(mockWindowDark)).toBe(true);

    const mockWindowLight = {
      matchMedia: vi.fn().mockReturnValue({ matches: false }),
    } as unknown as Window;
    expect(isBrowserDarkMode(mockWindowLight)).toBe(false);
  });
});
