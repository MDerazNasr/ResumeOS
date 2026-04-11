"use client";

import Link from "next/link";
import { useState } from "react";
import type { CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { getGoogleAuthStartUrl, logoutUser } from "@/lib/api/client";
import type { GoogleAuthStatusDto, UserDto } from "@/lib/api/types";

type AuthPanelProps = {
  user?: UserDto | null;
  googleAuth?: GoogleAuthStatusDto;
};

export function AuthPanel({ user, googleAuth }: AuthPanelProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogout() {
    setIsSubmitting(true);
    setError(null);

    try {
      await logoutUser();
      router.refresh();
    } catch (logoutError) {
      setError(logoutError instanceof Error ? logoutError.message : "Logout failed.");
      setIsSubmitting(false);
    }
  }

  if (user) {
    return (
      <section style={panelStyle}>
        <div style={{ display: "grid", gap: 6 }}>
          <strong style={{ fontSize: 16 }}>Signed In</strong>
          <span style={copyStyle}>
            {user.name} · {user.email}
          </span>
        </div>
        <div style={actionRowStyle}>
          <Link href="/app/settings" style={linkButtonStyle}>
            Settings
          </Link>
          <button disabled={isSubmitting} onClick={() => void handleLogout()} style={secondaryButtonStyle} type="button">
            {isSubmitting ? "Signing out..." : "Sign Out"}
          </button>
        </div>
        {error ? <p style={errorStyle}>{error}</p> : null}
      </section>
    );
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Sign In</strong>
        <span style={copyStyle}>
          Use Google to open your resumes, compile LaTeX, and review AI patch sets without managing a separate password.
        </span>
      </div>
      {googleAuth?.configured ? (
        <a href={getGoogleAuthStartUrl()} style={primaryLinkStyle}>
          Continue with Google
        </a>
      ) : (
        <p style={warningStyle}>
          Google sign-in is not configured yet. Set the Google OAuth environment variables on the API before trying to sign in.
        </p>
      )}
      {error ? <p style={errorStyle}>{error}</p> : null}
    </section>
  );
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 14,
  padding: 20,
  border: "1px solid var(--border)",
  borderRadius: 16,
  background: "var(--surface)"
};

const copyStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 14,
  lineHeight: 1.6
};

const actionRowStyle: CSSProperties = {
  display: "flex",
  gap: 10,
  flexWrap: "wrap",
};

const primaryButtonStyle: CSSProperties = {
  width: "fit-content",
  padding: "10px 14px",
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--accent-bg)",
  color: "var(--accent-fg)",
  cursor: "pointer"
};

const primaryLinkStyle: CSSProperties = {
  ...primaryButtonStyle,
  textDecoration: "none",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
};

const secondaryButtonStyle: CSSProperties = {
  ...primaryButtonStyle,
  background: "var(--surface)",
  color: "var(--fg)"
};

const linkButtonStyle: CSSProperties = {
  ...secondaryButtonStyle,
  textDecoration: "none",
  display: "inline-flex",
  alignItems: "center",
};

const errorStyle: CSSProperties = {
  margin: 0,
  color: "#ff8d8d",
  fontSize: 13
};

const warningStyle: CSSProperties = {
  margin: 0,
  color: "var(--muted)",
  fontSize: 13,
  lineHeight: 1.6,
};
