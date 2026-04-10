import { redirect } from "next/navigation";
import { SettingsPanel } from "@/components/auth/SettingsPanel";
import { getCurrentUser, getUserSettings } from "@/lib/api/client";

export default async function SettingsPage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/auth");
  }

  const settings = await getUserSettings();

  return <SettingsPanel settings={settings} user={user} />;
}
