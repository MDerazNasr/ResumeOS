import Link from "next/link";
import type { CSSProperties } from "react";
import type { ResumeDto } from "@/lib/api/types";

type ResumeListProps = {
  resumes: ResumeDto[];
};

export function ResumeList({ resumes }: ResumeListProps) {
  if (resumes.length === 0) {
    return (
      <div style={emptyStateStyle}>
        <p style={{ margin: 0, fontSize: 18 }}>No resumes yet.</p>
        <p style={{ margin: 0, color: "var(--muted)" }}>Create a master resume to start editing raw LaTeX.</p>
      </div>
    );
  }

  return (
    <div style={listStyle}>
      {resumes.map((resume) => (
        <Link href={`/app/resumes/${resume.id}`} key={resume.id} style={cardStyle}>
          <div style={{ display: "grid", gap: 6 }}>
            <strong style={{ fontSize: 18 }}>{resume.title}</strong>
            <span style={{ color: "var(--muted)", fontSize: 14 }}>{resume.slug}</span>
          </div>
          <span style={{ color: "var(--muted)", fontSize: 13 }}>
            Updated {new Date(resume.updatedAt).toLocaleString()}
          </span>
        </Link>
      ))}
    </div>
  );
}

const listStyle: CSSProperties = {
  display: "grid",
  gap: 16
};

const cardStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: 20,
  border: "1px solid var(--border)",
  borderRadius: 16,
  background: "var(--surface)"
};

const emptyStateStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  padding: 24,
  border: "1px dashed var(--border-strong)",
  borderRadius: 16,
  background: "var(--surface-elevated)"
};
