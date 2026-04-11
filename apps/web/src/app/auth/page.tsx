import { redirect } from "next/navigation";
import { AuthPanel } from "@/components/auth/AuthPanel";
import { getCurrentUser, getGoogleAuthStatus } from "@/lib/api/client";

export default async function AuthPage() {
  const [user, googleAuth] = await Promise.all([getCurrentUser(), getGoogleAuthStatus()]);

  if (user) {
    redirect("/app/resumes");
  }

  return (
    <main style={pageStyle}>
      <section style={cardStyle}>
        <div style={{ display: "grid", gap: 8 }}>
          <span style={eyebrowStyle}>Section 7</span>
          <h1 style={{ margin: 0, fontSize: 36 }}>Sign In to ResumeOS</h1>
          <p style={copyStyle}>
            Resume editing, snapshots, compile, and AI patch workflows now use a Google-backed session.
          </p>
        </div>
        <AuthPanel googleAuth={googleAuth} />
      </section>
    </main>
  );
}

const pageStyle = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  padding: 24,
};

const cardStyle = {
  width: "100%",
  maxWidth: 520,
  display: "grid",
  gap: 20,
};

const eyebrowStyle = {
  width: "fit-content",
  padding: "6px 10px",
  border: "1px solid #313748",
  borderRadius: 999,
  color: "#c8d0de",
  fontSize: 12,
  letterSpacing: "0.08em",
  textTransform: "uppercase" as const,
};

const copyStyle = {
  margin: 0,
  color: "#9ba3b4",
  fontSize: 16,
  lineHeight: 1.6,
};
