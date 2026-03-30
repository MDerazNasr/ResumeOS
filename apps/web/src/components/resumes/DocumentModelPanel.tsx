"use client";

import type { CSSProperties } from "react";
import type { DocumentModelDto } from "@/lib/api/types";

type DocumentModelPanelProps = {
  documentModel: DocumentModelDto;
};

export function DocumentModelPanel({ documentModel }: DocumentModelPanelProps) {
  const previewBlocks = documentModel.editableBlocks.slice(0, 6);

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Document Model</strong>
        <span style={{ color: "#9ba3b4", fontSize: 13 }}>
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
        {previewBlocks.length === 0 ? (
          <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
            No editable blocks were detected for the current draft.
          </p>
        ) : (
          previewBlocks.map((block) => (
            <div key={block.id} style={blockCardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                <strong style={{ fontSize: 13 }}>{block.label}</strong>
                <span style={badgeStyle}>{block.kind}</span>
              </div>
              <span style={{ color: "#9ba3b4", fontSize: 12 }}>
                Lines {block.startLine}-{block.endLine} • Col {block.startColumn}-{block.endColumn}
              </span>
              <p style={textPreviewStyle}>{block.text}</p>
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
  border: "1px solid #262b36",
  borderRadius: 16,
  background: "#12151c",
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
  border: "1px solid #262b36",
  borderRadius: 12,
  background: "#171a21",
};

const metricLabelStyle: CSSProperties = {
  color: "#9ba3b4",
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
  border: "1px solid #262b36",
  borderRadius: 12,
  background: "#171a21",
};

const badgeStyle: CSSProperties = {
  padding: "2px 8px",
  borderRadius: 999,
  background: "#1f2937",
  color: "#cfe2ff",
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
};

const textPreviewStyle: CSSProperties = {
  margin: 0,
  color: "#eef1f6",
  fontSize: 13,
  lineHeight: 1.5,
};
