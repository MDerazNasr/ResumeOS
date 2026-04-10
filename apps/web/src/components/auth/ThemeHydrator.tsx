"use client";

import { useEffect } from "react";

const THEME_STORAGE_KEY = "resumeos.themeMode";

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

export function inlineThemeScript() {
  return `
    (function () {
      try {
        var storedTheme = window.localStorage.getItem("${THEME_STORAGE_KEY}");
        if (storedTheme === "light" || storedTheme === "dark") {
          document.documentElement.dataset.theme = storedTheme;
        }
      } catch (error) {}
    })();
  `;
}
