"use client";

import { useMemo, useState } from "react";
import type { CSSProperties } from "react";
import type { DocumentModelDto, EditableBlockDto } from "@/lib/api/types";

type DocumentModelPanelProps = {
  documentModel: DocumentModelDto;
  onSuggestEdit: (block: EditableBlockDto, instruction: string) => Promise<void>;
};

export function DocumentModelPanel({ documentModel, onSuggestEdit }: DocumentModelPanelProps) {
  const previewBlocks = documentModel.editableBlocks.slice(0, 6);
  const initialInstructions = useMemo(
    () =>
      Object.fromEntries(
        previewBlocks.map((block) => [
          block.id,
          `Make this ${block.kind} stronger and more specific while preserving the existing voice.`,
        ]),
      ),
    [previewBlocks],
  );
  const [instructions, setInstructions] = useState<Record<string, string>>(initialInstructions);

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Document Model</strong>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>
          Protected structure is separated from AI-editable text blocks.
        </span>
      </div>
      <div style={metricsStyle}>
        <div style={metricCardStyle}>
          <span style={metricLabelStyle}>Protected Regions</span>
          <strong style={metricValueStyle}>{documentModel.protectedRegions.length}</strong>
        </div>
        <div style={metricCardStyle}>
          <span style={metricLabelStyle}>Editable Blocks</span>
          <strong style={metricValueStyle}>{documentModel.editableBlocks.length}</strong>
        </div>
      </div>
      <div style={{ display: "grid", gap: 10 }}>
        <strong style={{ fontSize: 14 }}>Detected Editable Blocks</strong>
        <span style={{ color: "var(--muted)", fontSize: 12 }}>
          Validation is currently strict: future patch targets must match one editable block exactly.
        </span>
        {previewBlocks.length === 0 ? (
          <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.6 }}>
            No editable blocks were detected for the current draft.
          </p>
        ) : (
          previewBlocks.map((block) => (
            <div key={block.id} style={blockCardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start" }}>
                <div style={{ display: "grid", gap: 4 }}>
                  <strong style={{ fontSize: 13 }}>{block.label}</strong>
                  <span style={{ color: "var(--muted)", fontSize: 12 }}>
                    Lines {block.startLine}-{block.endLine} • Col {block.startColumn}-{block.endColumn}
                  </span>
                </div>
                <div style={{ display: "grid", gap: 8, justifyItems: "end" }}>
                  <span style={badgeStyle}>{block.kind}</span>
                  <button
                    onClick={() => void onSuggestEdit(block, instructions[block.id] ?? initialInstructions[block.id])}
                    style={buttonStyle}
                    type="button"
                  >
                    Suggest Edit
                  </button>
                </div>
              </div>
              <p style={textPreviewStyle}>{block.text}</p>
              <label style={instructionLabelStyle}>
                Suggestion Prompt
                <textarea
                  onChange={(event) =>
                    setInstructions((current) => ({
                      ...current,
                      [block.id]: event.target.value,
                    }))
                  }
                  rows={3}
                  style={instructionInputStyle}
                  value={instructions[block.id] ?? initialInstructions[block.id]}
                />
              </label>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  padding: 20,
  border: "1px solid var(--border)",
  borderRadius: 16,
  background: "var(--surface-alt)",
};

const metricsStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: 10,
};

const metricCardStyle: CSSProperties = {
  display: "grid",
  gap: 4,
  padding: 12,
  border: "1px solid var(--border)",
  borderRadius: 12,
  background: "var(--metric-bg)",
};

const metricLabelStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
};

const metricValueStyle: CSSProperties = {
  fontSize: 22,
};

const blockCardStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  padding: 12,
  border: "1px solid var(--border)",
  borderRadius: 12,
  background: "var(--surface)",
};

const badgeStyle: CSSProperties = {
  padding: "2px 8px",
  borderRadius: 999,
  background: "var(--badge-bg)",
  color: "var(--badge-fg)",
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
};

const buttonStyle: CSSProperties = {
  padding: "6px 10px",
  border: "1px solid #3b4254",
  borderRadius: 10,
  background: "var(--surface)",
  color: "var(--fg)",
  cursor: "pointer",
  fontSize: 12,
};

const textPreviewStyle: CSSProperties = {
  margin: 0,
  color: "var(--fg)",
  fontSize: 13,
  lineHeight: 1.5,
};

const instructionLabelStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  color: "var(--muted)",
  fontSize: 12,
};

const instructionInputStyle: CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--surface-input)",
  color: "var(--fg)",
  resize: "vertical",
  fontSize: 12,
  lineHeight: 1.5,
};
