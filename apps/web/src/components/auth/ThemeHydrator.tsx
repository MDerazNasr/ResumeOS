"use client";

import { useEffect } from "react";

export const THEME_STORAGE_KEY = "resumeos.themeMode";

type ThemeHydratorProps = {
  themeMode: "dark" | "light";
};

export function ThemeHydrator({ themeMode }: ThemeHydratorProps) {
  useEffect(() => {
    document.documentElement.dataset.theme = themeMode;
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, themeMode);
    } catch {
      return;
    }
  }, [themeMode]);

  return null;
}
