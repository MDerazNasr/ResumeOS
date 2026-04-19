"use client";

import type { CSSProperties } from "react";
import type { HolisticReviewContextDto } from "@/lib/api/types";

type HolisticReviewPanelProps = {
  context: HolisticReviewContextDto;
};

export function HolisticReviewPanel({ context }: HolisticReviewPanelProps) {
  return (
    <div style={panelStyle}>
      <div style={{ display: "grid", gap: 4 }}>
        <strong style={{ fontSize: 15 }}>Holistic Review Context</strong>
        <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.5 }}>
          This is the PDF plus LaTeX review boundary. The next AI slice can use this context to reason about structure,
          flow, and formatting constraints without bypassing patch review.
        </p>
      </div>
      <div style={statsGridStyle}>
        <div style={statCardStyle}>
          <span style={labelStyle}>Latest Compile</span>
          <strong style={{ fontSize: 16 }}>
            {context.latestCompileStatus ? (context.latestCompileStatus === "success" ? "Ready" : "Error") : "Missing"}
          </strong>
          <span style={valueHintStyle}>
            {context.latestCompiledAt ? new Date(context.latestCompiledAt).toLocaleString() : "Compile once to attach a PDF artifact."}
          </span>
        </div>
        <div style={statCardStyle}>
          <span style={labelStyle}>Source Lines</span>
          <strong style={{ fontSize: 16 }}>{context.sourceLineCount}</strong>
          <span style={valueHintStyle}>Current LaTeX draft length.</span>
        </div>
        <div style={statCardStyle}>
          <span style={labelStyle}>Editable Blocks</span>
          <strong style={{ fontSize: 16 }}>{context.editableBlockCount}</strong>
          <span style={valueHintStyle}>Safe content blocks available for AI edits.</span>
        </div>
        <div style={statCardStyle}>
          <span style={labelStyle}>PDF Pages</span>
          <strong style={{ fontSize: 16 }}>{context.pdfPageCount ?? "?"}</strong>
          <span style={valueHintStyle}>
            {context.pdfSizeKb ? `${context.pdfSizeKb} KB artifact` : "Compile to derive rendered review signals."}
          </span>
        </div>
      </div>
      <div style={{ display: "grid", gap: 8 }}>
        <span style={labelStyle}>Reviewable Focus Areas</span>
        <div style={chipWrapStyle}>
          {context.editableBlockLabels.length > 0 ? (
            context.editableBlockLabels.map((label) => (
              <span key={label} style={chipStyle}>
                {label}
              </span>
            ))
          ) : (
            <span style={valueHintStyle}>No editable blocks detected yet.</span>
          )}
        </div>
        <span style={valueHintStyle}>
          {context.pdfUrl
            ? "A compiled PDF artifact is available, so the next slice can add rendered-review grounding."
            : "No compiled PDF artifact is available yet, so review is currently source-only."}
        </span>
        {context.layoutSignals.length > 0 ? (
          <div style={{ display: "grid", gap: 8 }}>
            <span style={labelStyle}>Rendered Signals</span>
            <div style={chipWrapStyle}>
              {context.layoutSignals.map((signal) => (
                <span key={signal} style={chipStyle}>
                  {signal}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  padding: 16,
  borderRadius: 16,
  border: "1px solid var(--border-strong)",
  background: "var(--surface-elevated)"
};

const statsGridStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))"
};

const statCardStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  padding: 12,
  borderRadius: 12,
  background: "var(--surface-muted)",
  border: "1px solid var(--border-subtle)"
};

const labelStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: "0.08em"
};

const valueHintStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 12,
  lineHeight: 1.5
};

const chipWrapStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 8
};

const chipStyle: CSSProperties = {
  padding: "6px 10px",
  borderRadius: 999,
  background: "var(--surface-muted)",
  border: "1px solid var(--border-subtle)",
  fontSize: 12
};
