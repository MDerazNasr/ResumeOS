"use client";

import { useMemo, useState } from "react";
import type { CSSProperties } from "react";
import { saveDraft } from "@/lib/api/client";
import type { ResumeDto, WorkingDraftDto } from "@/lib/api/types";

type ResumeEditorProps = {
  draft: WorkingDraftDto;
  resume: ResumeDto;
};

export function ResumeEditor({ draft, resume }: ResumeEditorProps) {
  const [sourceTex, setSourceTex] = useState(draft.sourceTex);
  const [version, setVersion] = useState(draft.version);
  const [updatedAt, setUpdatedAt] = useState(draft.updatedAt);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isDirty = useMemo(() => sourceTex !== draft.sourceTex, [draft.sourceTex, sourceTex]);

  async function handleSave() {
    setIsSaving(true);
    setError(null);

    try {
      const savedDraft = await saveDraft(resume.id, { sourceTex, version });
      setVersion(savedDraft.version);
      setUpdatedAt(savedDraft.updatedAt);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save draft.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section style={shellStyle}>
      <div style={headerStyle}>
        <div style={{ display: "grid", gap: 4 }}>
          <h1 style={{ margin: 0, fontSize: 28 }}>{resume.title}</h1>
          <p style={{ margin: 0, color: "#9ba3b4" }}>Editing raw LaTeX working draft</p>
        </div>
        <div style={{ display: "grid", justifyItems: "end", gap: 8 }}>
          <button disabled={isSaving || !isDirty} onClick={handleSave} style={buttonStyle} type="button">
            {isSaving ? "Saving..." : "Save Draft"}
          </button>
          <span style={{ color: isDirty ? "#f6d36e" : "#9ba3b4", fontSize: 13 }}>
            {isDirty ? "Unsaved changes" : `Saved ${new Date(updatedAt).toLocaleString()}`}
          </span>
        </div>
      </div>
      <textarea onChange={(event) => setSourceTex(event.target.value)} style={textareaStyle} value={sourceTex} />
      <div style={footerStyle}>
        <span style={{ color: "#9ba3b4", fontSize: 13 }}>Draft version {version}</span>
        {error ? <span style={{ color: "#ff8d8d", fontSize: 13 }}>{error}</span> : null}
      </div>
    </section>
  );
}

const shellStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  width: "100%",
  maxWidth: 1200,
  margin: "0 auto",
  padding: 32
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 24,
  alignItems: "flex-start"
};

const buttonStyle: CSSProperties = {
  padding: "10px 14px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#eef1f6",
  color: "#0f1115",
  cursor: "pointer"
};

const textareaStyle: CSSProperties = {
  minHeight: "70vh",
  width: "100%",
  padding: 20,
  border: "1px solid #262b36",
  borderRadius: 16,
  background: "#12151c",
  color: "#eef1f6",
  fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
  fontSize: 14,
  lineHeight: 1.6,
  resize: "vertical"
};

const footerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12
};
