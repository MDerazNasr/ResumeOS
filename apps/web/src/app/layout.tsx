import "./globals.css";
import type { ReactNode } from "react";
import { ThemeHydrator } from "@/components/auth/ThemeHydrator";
import { inlineThemeScript } from "@/components/auth/themeScript";
import { getCurrentUser, getUserSettings } from "@/lib/api/client";

export const metadata = {
  title: "ResumeOS",
  description: "AI-assisted resume IDE"
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();
  const themeMode = user ? (await getUserSettings()).themeMode : "light";

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
