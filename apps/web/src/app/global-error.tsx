"use client";

import type { CSSProperties } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body style={bodyStyle}>
        <main style={shellStyle}>
          <div style={cardStyle}>
            <span style={eyebrowStyle}>Global Error</span>
            <h1 style={{ margin: 0, fontSize: 32 }}>ResumeOS failed to render.</h1>
            <p style={copyStyle}>
              {error.message || "A global rendering error occurred."}
            </p>
            <button onClick={reset} style={buttonStyle} type="button">
              Retry
            </button>
          </div>
        </main>
      </body>
    </html>
  );
}

const bodyStyle: CSSProperties = {
  margin: 0,
  background: "var(--bg)",
  color: "var(--fg)",
  fontFamily: 'Geist, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
};

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
