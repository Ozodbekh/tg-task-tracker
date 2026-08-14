import { useEffect, useState } from "react";

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);

  useEffect(() => {
    const media = window.matchMedia(query);
    const listener = (event: MediaQueryListEvent) => setMatches(event.matches);
    setMatches(media.matches);
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, [query]);

  return matches;
}

export function useBreakpoints(): { mobile: boolean; tablet: boolean } {
  return {
    mobile: useMediaQuery("(max-width: 640px)"),
    tablet: useMediaQuery("(max-width: 1024px)"),
  };
}
