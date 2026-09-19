/**
 * Dynamic Favicon Switcher based on Browser Color Scheme.
 *
 * When browser is in dark mode (dark tab bar):
 *   Uses the light logo (white verification arm #FFFFFF, vibrant coral #F29472).
 * When browser is in light mode (light tab bar):
 *   Uses the dark logo (ink black verification arm #1E1B18, deep coral #E27855).
 */

export type FaviconMode = "dark" | "light";

export interface FaviconLinkItem {
  id: string;
  rel: string;
  type?: string;
  sizes?: string;
  href: (mode: FaviconMode) => string;
}

export const FAVICON_ITEMS: FaviconLinkItem[] = [
  {
    id: "favicon-svg",
    rel: "icon",
    type: "image/svg+xml",
    href: (m) => `/favicon-${m}.svg?v=${m}`,
  },
  {
    id: "favicon-32",
    rel: "icon",
    type: "image/png",
    sizes: "32x32",
    href: (m) => `/favicon-${m}-32x32.png?v=${m}`,
  },
  {
    id: "favicon-16",
    rel: "icon",
    type: "image/png",
    sizes: "16x16",
    href: (m) => `/favicon-${m}-16x16.png?v=${m}`,
  },
  {
    id: "favicon-ico",
    rel: "shortcut icon",
    href: (m) => `/favicon-${m}.ico?v=${m}`,
  },
];

export function isBrowserDarkMode(targetWindow: Window = window): boolean {
  if (typeof targetWindow === "undefined" || !targetWindow.matchMedia) {
    return false;
  }
  return targetWindow.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function updateFavicon(isDark: boolean, targetDoc: Document = document): void {
  if (!targetDoc || !targetDoc.head) return;
  const mode: FaviconMode = isDark ? "dark" : "light";

  FAVICON_ITEMS.forEach((item) => {
    const newHref = item.href(mode);
    const existing = targetDoc.getElementById(item.id) as HTMLLinkElement | null;

    if (existing) {
      if (existing.getAttribute("href") === newHref) {
        return;
      }
      const el = targetDoc.createElement("link");
      el.id = item.id;
      el.setAttribute("rel", item.rel);
      if (item.type) el.setAttribute("type", item.type);
      if (item.sizes) el.setAttribute("sizes", item.sizes);
      el.setAttribute("href", newHref);
      existing.parentNode?.replaceChild(el, existing);
    } else {
      const el = targetDoc.createElement("link");
      el.id = item.id;
      el.setAttribute("rel", item.rel);
      if (item.type) el.setAttribute("type", item.type);
      if (item.sizes) el.setAttribute("sizes", item.sizes);
      el.setAttribute("href", newHref);
      targetDoc.head.appendChild(el);
    }
  });
}

export function initFaviconSwitcher(targetWindow: Window = window): () => void {
  if (!targetWindow || !targetWindow.matchMedia) {
    return () => {};
  }

  const mediaQuery = targetWindow.matchMedia("(prefers-color-scheme: dark)");

  // Set initial favicon according to browser color scheme
  updateFavicon(mediaQuery.matches, targetWindow.document);

  const listener = (event: MediaQueryListEvent) => {
    updateFavicon(event.matches, targetWindow.document);
  };

  if (typeof mediaQuery.addEventListener === "function") {
    mediaQuery.addEventListener("change", listener);
    return () => mediaQuery.removeEventListener("change", listener);
  } else if (typeof (mediaQuery as unknown as { addListener?: (cb: (e: MediaQueryListEvent) => void) => void }).addListener === "function") {
    const mq = mediaQuery as unknown as {
      addListener: (cb: (e: MediaQueryListEvent) => void) => void;
      removeListener: (cb: (e: MediaQueryListEvent) => void) => void;
    };
    mq.addListener(listener);
    return () => mq.removeListener(listener);
  }

  return () => {};
}
