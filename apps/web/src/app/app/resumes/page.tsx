import type { CSSProperties } from "react";
import { redirect } from "next/navigation";
import { AuthPanel } from "@/components/auth/AuthPanel";
import { CreateResumeForm } from "@/components/resumes/CreateResumeForm";
import { ResumeList } from "@/components/resumes/ResumeList";
import { getCurrentUser, listResumes } from "@/lib/api/client";

export default async function ResumesPage() {
  const user = await getCurrentUser();

  if (user.authSource !== "session") {
    redirect("/auth");
  }

  const resumeList = await listResumes();

  return (
    <main style={pageStyle}>
      <section style={heroStyle}>
        <div style={{ display: "grid", gap: 8 }}>
          <span style={eyebrowStyle}>Section 1</span>
          <h1 style={{ margin: 0, fontSize: 40 }}>Resume Document Core</h1>
          <p style={copyStyle}>
            {user.name} can create a resume, edit the raw LaTeX draft, and reopen the exact saved source later.
          </p>
        </div>
        <div style={heroSidebarStyle}>
          <AuthPanel user={user} />
          <CreateResumeForm />
        </div>
      </section>
      <section style={{ display: "grid", gap: 16 }}>
        <h2 style={{ margin: 0, fontSize: 20 }}>Your Resumes</h2>
        <ResumeList resumes={resumeList.items} />
      </section>
    </main>
  );
}

const pageStyle: CSSProperties = {
  display: "grid",
  gap: 32,
  width: "100%",
  maxWidth: 1200,
  margin: "0 auto",
  padding: 32
};

const heroStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "minmax(0, 1.2fr) minmax(320px, 0.8fr)",
  gap: 20
};

const heroSidebarStyle: CSSProperties = {
  display: "grid",
  gap: 16
};

const eyebrowStyle: CSSProperties = {
  width: "fit-content",
  padding: "6px 10px",
  border: "1px solid #313748",
  borderRadius: 999,
  color: "#c8d0de",
  fontSize: 12,
  letterSpacing: "0.08em",
  textTransform: "uppercase"
};

const copyStyle: CSSProperties = {
  maxWidth: 760,
  margin: 0,
  color: "#9ba3b4",
  fontSize: 16,
  lineHeight: 1.6
};
