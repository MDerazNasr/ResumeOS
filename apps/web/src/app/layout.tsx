import "./globals.css";
import type { ReactNode } from "react";
import { ThemeHydrator, inlineThemeScript } from "@/components/auth/ThemeHydrator";
import { getCurrentUser, getUserSettings } from "@/lib/api/client";

export const metadata = {
  title: "ResumeOS",
  description: "AI-assisted resume IDE"
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();
  const themeMode = user ? (await getUserSettings()).themeMode : "dark";

  return (
    <html data-theme={themeMode} lang="en">
      <body>
        <script dangerouslySetInnerHTML={{ __html: inlineThemeScript() }} />
        <ThemeHydrator themeMode={themeMode} />
        {children}
      </body>
    </html>
  );
}
