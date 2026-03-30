"use client";

import type { CSSProperties } from "react";
import { buildLineDiff } from "@/components/resumes/lineDiff";

type SnapshotCompareViewProps = {
  snapshotName: string;
  snapshotSource: string;
  currentSource: string;
  onClose: () => void;
};

export function SnapshotCompareView({
  snapshotName,
  snapshotSource,
  currentSource,
  onClose,
}: SnapshotCompareViewProps) {
  const diffLines = buildLineDiff(snapshotSource, currentSource);

  return (
    <section style={panelStyle}>
      <div style={headerStyle}>
        <div style={{ display: "grid", gap: 4 }}>
          <strong style={{ fontSize: 15 }}>Compare Snapshot</strong>
          <span style={{ color: "#9ba3b4", fontSize: 12 }}>
            {snapshotName} vs current working draft
          </span>
        </div>
        <button onClick={onClose} style={buttonStyle} type="button">
          Close
        </button>
      </div>
      <div style={legendStyle}>
        <span style={{ color: "#9fe0b0" }}>+ Added in current draft</span>
        <span style={{ color: "#ffb0b0" }}>- Removed from snapshot</span>
        <span style={{ color: "#9ba3b4" }}>= Unchanged</span>
      </div>
      <div style={diffContainerStyle}>
        {diffLines.map((line, index) => (
          <div key={`${line.type}-${index}`} style={lineStyle(line.type)}>
            <span style={markerStyle}>{lineMarker(line.type)}</span>
            <code style={codeStyle}>{line.text || " "}</code>
          </div>
        ))}
      </div>
    </section>
  );
}

function lineMarker(type: "added" | "removed" | "unchanged") {
  if (type === "added") {
    return "+";
  }

  if (type === "removed") {
    return "-";
  }

  return "=";
}

function lineStyle(type: "added" | "removed" | "unchanged"): CSSProperties {
  const baseStyle: CSSProperties = {
    display: "grid",
    gridTemplateColumns: "16px minmax(0, 1fr)",
    gap: 10,
    padding: "6px 10px",
    borderRadius: 10,
    alignItems: "start",
  };

  if (type === "added") {
    return { ...baseStyle, background: "#13261a", color: "#dff7e5" };
  }

  if (type === "removed") {
    return { ...baseStyle, background: "#2a1417", color: "#ffe1e1" };
  }

  return { ...baseStyle, background: "#141820", color: "#9ba3b4" };
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  padding: 16,
  border: "1px solid #262b36",
  borderRadius: 14,
  background: "#171a21",
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12,
  alignItems: "center",
};

const buttonStyle: CSSProperties = {
  padding: "8px 12px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#12151c",
  color: "#eef1f6",
  cursor: "pointer",
};

const legendStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 12,
  fontSize: 12,
};

const diffContainerStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  maxHeight: 300,
  overflow: "auto",
};

const markerStyle: CSSProperties = {
  display: "inline-flex",
  justifyContent: "center",
  fontWeight: 700,
  fontSize: 13,
  paddingTop: 2,
};

const codeStyle: CSSProperties = {
  margin: 0,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  fontFamily: "var(--font-geist-mono, monospace)",
  fontSize: 12,
  lineHeight: 1.5,
};
