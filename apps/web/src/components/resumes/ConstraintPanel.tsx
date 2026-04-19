"use client";

import { useMemo, useState } from "react";
import type { CSSProperties } from "react";
import { updateResumeConstraints } from "@/lib/api/client";
import type { ResumeConstraintsDto } from "@/lib/api/types";

type ConstraintPanelProps = {
  initialConstraints: ResumeConstraintsDto;
  resumeId: string;
};

export function ConstraintPanel({ initialConstraints, resumeId }: ConstraintPanelProps) {
  const [draftValue, setDraftValue] = useState(initialConstraints.rules.join("\n"));
  const [savedRules, setSavedRules] = useState(initialConstraints.rules);
  const [updatedAt, setUpdatedAt] = useState(initialConstraints.updatedAt);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const normalizedRules = useMemo(
    () =>
      draftValue
        .split("\n")
        .map((rule) => rule.trim())
        .filter(Boolean),
    [draftValue],
  );

  const isDirty = JSON.stringify(normalizedRules) !== JSON.stringify(savedRules);

  async function handleSave() {
    setIsSaving(true);
    setError(null);
    setStatus(null);

    try {
      const updated = await updateResumeConstraints(resumeId, { rules: normalizedRules });
      setSavedRules(updated.rules);
      setDraftValue(updated.rules.join("\n"));
      setUpdatedAt(updated.updatedAt);
      setStatus("Saved");
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Failed to save rules.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 4 }}>
        <strong style={{ fontSize: 15 }}>Constraints</strong>
        <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.5 }}>
          One rule per line. These apply across edit, review, holistic review, and tailoring.
        </p>
      </div>
      <textarea
        onChange={(event) => setDraftValue(event.target.value)}
        placeholder={"Keep each bullet to one line.\nPrefer concise wording.\nAvoid first-person voice."}
        style={textareaStyle}
        value={draftValue}
      />
      <div style={footerStyle}>
        <span style={{ color: error ? "var(--diff-remove-fg)" : "var(--muted)", fontSize: 12 }}>
          {error
            ? error
            : isSaving
              ? "Saving..."
              : isDirty
                ? "Unsaved rule changes."
                : status ?? `Saved ${new Date(updatedAt).toLocaleString()}`}
        </span>
        <button
          disabled={isSaving || !isDirty}
          onClick={() => void handleSave()}
          style={buttonStyle}
          type="button"
        >
          {isSaving ? "Saving..." : "Save Rules"}
        </button>
      </div>
    </section>
  );
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  padding: 16,
  borderRadius: 16,
  border: "1px solid var(--border-strong)",
  background: "var(--surface-elevated)"
};

const textareaStyle: CSSProperties = {
  width: "100%",
  minHeight: 120,
  resize: "vertical",
  padding: 12,
  borderRadius: 12,
  border: "1px solid var(--border-strong)",
  background: "var(--surface-muted)",
  color: "var(--foreground)",
  fontFamily: "inherit",
  fontSize: 14,
  lineHeight: 1.5
};

const footerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12,
  alignItems: "center"
};

const buttonStyle: CSSProperties = {
  padding: "10px 14px",
  borderRadius: 12,
  border: "1px solid var(--border-strong)",
  background: "var(--surface-muted)",
  color: "var(--foreground)",
  fontWeight: 600,
  cursor: "pointer"
};
