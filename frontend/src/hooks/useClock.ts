import { useCallback, useEffect, useRef, useState } from "react";

export function useClock() {
  const [now, setNow] = useState(() => new Date());
  const rafRef = useRef<number>(0);

  const tick = useCallback(() => {
    setNow(new Date());
    rafRef.current = requestAnimationFrame(tick);
  }, []);

  useEffect(() => {
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [tick]);

  return now;
}
