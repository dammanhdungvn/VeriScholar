import { useState, useRef, useCallback, useEffect } from "react";

/**
 * Zero-Jank Token Stream Buffer using requestAnimationFrame
 * Simulates real-time LLM token generation smoothly at 60fps without causing React render storms.
 */
export function useDemoStream(fullText: string, speedMs: number = 18) {
  const [displayedText, setDisplayedText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const indexRef = useRef(0);
  const rafIdRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);

  const startStream = useCallback(() => {
    if (rafIdRef.current !== null) {
      cancelAnimationFrame(rafIdRef.current);
      rafIdRef.current = null;
    }

    indexRef.current = 0;
    lastTimeRef.current = performance.now();

    rafIdRef.current = requestAnimationFrame((currentTime: number) => {
      setDisplayedText("");
      setIsStreaming(true);
      lastTimeRef.current = currentTime;

      const loop = (time: number) => {
        const delta = time - lastTimeRef.current;
        if (delta >= speedMs) {
          lastTimeRef.current = time;
          indexRef.current = Math.min(indexRef.current + 8, fullText.length);
          setDisplayedText(fullText.slice(0, indexRef.current));
        }

        if (indexRef.current < fullText.length) {
          rafIdRef.current = requestAnimationFrame(loop);
        } else {
          setIsStreaming(false);
          rafIdRef.current = null;
        }
      };

      rafIdRef.current = requestAnimationFrame(loop);
    });
  }, [fullText, speedMs]);

  useEffect(() => {
    startStream();
    return () => {
      if (rafIdRef.current !== null) {
        cancelAnimationFrame(rafIdRef.current);
        rafIdRef.current = null;
      }
    };
  }, [startStream]);

  return { displayedText, isStreaming, startStream };
}
