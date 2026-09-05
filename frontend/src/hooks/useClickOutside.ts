import { useEffect, useRef } from "react";

export function useClickOutside<T extends HTMLElement>(onOutsideClick: () => void, active: boolean) {
  const ref = useRef<T | null>(null);

  useEffect(() => {
    if (!active) return;

    function handlePointerDown(event: PointerEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        onOutsideClick();
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [active, onOutsideClick]);

  return ref;
}
