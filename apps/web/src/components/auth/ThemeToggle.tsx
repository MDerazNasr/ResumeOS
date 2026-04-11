"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import { updateUserSettings } from "@/lib/api/client";

type ThemeToggleProps = {
  initialThemeMode: "dark" | "light";
};

export function ThemeToggle({ initialThemeMode }: ThemeToggleProps) {
  const [themeMode, setThemeMode] = useState(initialThemeMode);
  const [isSaving, setIsSaving] = useState(false);

  async function handleToggle() {
    const nextTheme = themeMode === "dark" ? "light" : "dark";
    const previousTheme = themeMode;
    setThemeMode(nextTheme);
    setIsSaving(true);

    document.documentElement.dataset.theme = nextTheme;
    try {
      window.localStorage.setItem("resumeos.themeMode", nextTheme);
    } catch {
      // best-effort cache only
    }

    try {
      await updateUserSettings({ themeMode: nextTheme });
    } catch {
      setThemeMode(previousTheme);
      document.documentElement.dataset.theme = previousTheme;
      try {
        window.localStorage.setItem("resumeos.themeMode", previousTheme);
      } catch {
        // best-effort cache only
      }
    } finally {
      setIsSaving(false);
    }
  }

  const checked = themeMode === "light";

  return (
    <button aria-label="Toggle light mode" disabled={isSaving} onClick={() => void handleToggle()} style={buttonStyle} type="button">
      <span style={labelStyle}>{checked ? "Light" : "Dark"}</span>
      <span aria-hidden="true" style={trackStyle(checked)}>
        <span style={thumbStyle(checked)} />
      </span>
    </button>
  );
}

const buttonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 10,
  padding: "8px 10px",
  border: "1px solid var(--border-strong)",
  borderRadius: 999,
  background: "var(--surface)",
  color: "var(--fg)",
  cursor: "pointer",
};

const labelStyle: CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
};

function trackStyle(checked: boolean): CSSProperties {
  return {
    position: "relative",
    display: "inline-flex",
    width: 40,
    height: 22,
    borderRadius: 999,
    background: checked ? "var(--accent-bg)" : "var(--border-strong)",
    transition: "background 120ms ease",
    alignItems: "center",
  };
}

function thumbStyle(checked: boolean): CSSProperties {
  return {
    width: 16,
    height: 16,
    borderRadius: "50%",
    background: checked ? "var(--accent-fg)" : "var(--fg)",
    transform: `translateX(${checked ? "20px" : "3px"})`,
    transition: "transform 120ms ease",
  };
}
