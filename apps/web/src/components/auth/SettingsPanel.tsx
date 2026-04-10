"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { CSSProperties } from "react";
import { logoutUser, updateUserSettings } from "@/lib/api/client";
import type { UserDto, UserSettingsDto } from "@/lib/api/types";

type SettingsPanelProps = {
  user: UserDto;
  settings: UserSettingsDto;
};

export function SettingsPanel({ user, settings }: SettingsPanelProps) {
  const router = useRouter();
  const [editorMode, setEditorMode] = useState(settings.editorMode);
  const [isSaving, setIsSaving] = useState(false);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  async function handleModeChange(nextMode: "standard" | "vim") {
    if (nextMode === editorMode) {
      return;
    }

    const previousMode = editorMode;
    setEditorMode(nextMode);
    setIsSaving(true);
    setError(null);
    setStatus(null);

    try {
      await updateUserSettings({ editorMode: nextMode });
      setStatus("Saved");
    } catch (updateError) {
      setEditorMode(previousMode);
      setError(updateError instanceof Error ? updateError.message : "Failed to update settings.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleLogout() {
    setIsSigningOut(true);
    setError(null);

    try {
      await logoutUser();
      router.push("/auth");
      router.refresh();
    } catch (logoutError) {
      setError(logoutError instanceof Error ? logoutError.message : "Logout failed.");
      setIsSigningOut(false);
    }
  }

  return (
    <section style={pageStyle}>
      <div style={cardStyle}>
        <div style={{ display: "grid", gap: 6 }}>
          <span style={eyebrowStyle}>Section 7</span>
          <h1 style={{ margin: 0, fontSize: 32 }}>Settings</h1>
          <p style={copyStyle}>Manage your account session and editor preferences.</p>
        </div>

        <div style={sectionStyle}>
          <strong style={sectionTitleStyle}>Account</strong>
          <div style={metaRowStyle}>
            <span>{user.name}</span>
            <span style={metaMutedStyle}>{user.email}</span>
          </div>
          <div style={buttonRowStyle}>
            <Link href="/app/resumes" style={secondaryLinkStyle}>
              Back to resumes
            </Link>
            <button disabled={isSigningOut} onClick={() => void handleLogout()} style={secondaryButtonStyle} type="button">
              {isSigningOut ? "Signing out..." : "Sign out"}
            </button>
          </div>
        </div>

        <div style={sectionStyle}>
          <strong style={sectionTitleStyle}>Editor Mode</strong>
          <div style={toggleRowStyle}>
            <button onClick={() => void handleModeChange("standard")} style={toggleButtonStyle(editorMode === "standard")} type="button">
              Standard
            </button>
            <button onClick={() => void handleModeChange("vim")} style={toggleButtonStyle(editorMode === "vim")} type="button">
              Vim
            </button>
          </div>
          <span style={metaMutedStyle}>{isSaving ? "Saving..." : status ?? "Stored in your account settings"}</span>
        </div>

        {error ? <p style={errorStyle}>{error}</p> : null}
      </div>
    </section>
  );
}

const pageStyle: CSSProperties = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  padding: 24,
};

const cardStyle: CSSProperties = {
  width: "100%",
  maxWidth: 560,
  display: "grid",
  gap: 20,
  padding: 24,
  border: "1px solid #262b36",
  borderRadius: 18,
  background: "#171a21",
};

const sectionStyle: CSSProperties = {
  display: "grid",
  gap: 10,
  paddingTop: 4,
};

const sectionTitleStyle: CSSProperties = {
  fontSize: 16,
};

const eyebrowStyle: CSSProperties = {
  width: "fit-content",
  padding: "6px 10px",
  border: "1px solid #313748",
  borderRadius: 999,
  color: "#c8d0de",
  fontSize: 12,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
};

const copyStyle: CSSProperties = {
  margin: 0,
  color: "#9ba3b4",
  fontSize: 15,
  lineHeight: 1.6,
};

const metaRowStyle: CSSProperties = {
  display: "grid",
  gap: 4,
  color: "#eef1f6",
};

const metaMutedStyle: CSSProperties = {
  color: "#9ba3b4",
  fontSize: 13,
};

const buttonRowStyle: CSSProperties = {
  display: "flex",
  gap: 10,
  flexWrap: "wrap",
};

const toggleRowStyle: CSSProperties = {
  display: "inline-flex",
  gap: 8,
};

const secondaryButtonStyle: CSSProperties = {
  padding: "10px 14px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#171a21",
  color: "#eef1f6",
  cursor: "pointer",
};

const secondaryLinkStyle: CSSProperties = {
  ...secondaryButtonStyle,
  textDecoration: "none",
  display: "inline-flex",
  alignItems: "center",
};

function toggleButtonStyle(isActive: boolean): CSSProperties {
  return {
    padding: "10px 14px",
    border: `1px solid ${isActive ? "#7fa4ff" : "#3b4254"}`,
    borderRadius: 12,
    background: isActive ? "#18253d" : "#171a21",
    color: isActive ? "#dce8ff" : "#eef1f6",
    cursor: "pointer",
    fontWeight: 600,
  };
}

const errorStyle: CSSProperties = {
  margin: 0,
  color: "#ff8d8d",
  fontSize: 13,
};
