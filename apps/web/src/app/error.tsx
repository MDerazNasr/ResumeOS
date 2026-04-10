"use client";

import type { CSSProperties } from "react";

type ErrorPageProps = {
  error: Error & { digest?: string };
  reset: () => void;
};

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  return (
    <main style={shellStyle}>
      <div style={cardStyle}>
        <span style={eyebrowStyle}>App Error</span>
        <h1 style={{ margin: 0, fontSize: 32 }}>The page hit a runtime error.</h1>
        <p style={copyStyle}>
          {error.message || "An unexpected error occurred while rendering the current route."}
        </p>
        <button onClick={reset} style={buttonStyle} type="button">
          Try Again
        </button>
      </div>
    </main>
  );
}

const shellStyle: CSSProperties = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  padding: 32,
};

const cardStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  width: "100%",
  maxWidth: 640,
  padding: 28,
  border: "1px solid var(--border)",
  borderRadius: 18,
  background: "var(--surface)",
};

const eyebrowStyle: CSSProperties = {
  width: "fit-content",
  padding: "6px 10px",
  border: "1px solid var(--border-strong)",
  borderRadius: 999,
  color: "var(--soft)",
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
};

const copyStyle: CSSProperties = {
  margin: 0,
  color: "var(--muted)",
  lineHeight: 1.6,
};

const buttonStyle: CSSProperties = {
  width: "fit-content",
  padding: "10px 14px",
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--accent-bg)",
  color: "var(--accent-fg)",
  cursor: "pointer",
};
