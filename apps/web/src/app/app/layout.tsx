import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import { redirect } from "next/navigation";
import { ThemeToggle } from "@/components/auth/ThemeToggle";
import { getCurrentUser, getUserSettings } from "@/lib/api/client";

export default async function AppLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/auth");
  }

  const settings = await getUserSettings();

  return (
    <div style={shellStyle}>
      <header style={headerStyle}>
        <div style={{ display: "grid", gap: 2 }}>
          <Link href="/app/resumes" style={brandStyle}>
            ResumeOS
          </Link>
          <span style={metaStyle}>{user.email}</span>
        </div>
        <div style={headerActionsStyle}>
          <ThemeToggle initialThemeMode={settings.themeMode} />
          <Link href="/app/settings" style={settingsLinkStyle}>
            Settings
          </Link>
        </div>
      </header>
      {children}
    </div>
  );
}

const shellStyle: CSSProperties = {
  minHeight: "100vh",
  display: "grid",
  gridTemplateRows: "auto 1fr",
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 16,
  padding: "16px 24px",
  borderBottom: "1px solid var(--border)",
  background: "var(--surface)",
  position: "sticky",
  top: 0,
  zIndex: 20,
};

const brandStyle: CSSProperties = {
  fontSize: 18,
  fontWeight: 700,
  textDecoration: "none",
};

const metaStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 13,
};

const headerActionsStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
};

const settingsLinkStyle: CSSProperties = {
  padding: "8px 10px",
  border: "1px solid var(--border-strong)",
  borderRadius: 999,
  background: "var(--surface)",
  color: "var(--fg)",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 600,
};
