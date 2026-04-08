"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import type { MockPatchProposalDto } from "@/lib/api/types";

type MockPatchPanelProps = {
  onApply: (proposal: MockPatchProposalDto) => Promise<boolean>;
  proposals: MockPatchProposalDto[];
};

export function MockPatchPanel({ onApply, proposals }: MockPatchPanelProps) {
  const [dismissedIds, setDismissedIds] = useState<string[]>([]);
  const [applyingId, setApplyingId] = useState<string | null>(null);
  const visibleProposals = proposals.filter((proposal) => !dismissedIds.includes(proposal.id));

  async function handleApply(proposal: MockPatchProposalDto) {
    setApplyingId(proposal.id);

    try {
      const applied = await onApply(proposal);
      if (applied) {
        setDismissedIds((current) => [...current, proposal.id]);
      }
    } finally {
      setApplyingId(null);
    }
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Mock Patch Review</strong>
        <span style={{ color: "#9ba3b4", fontSize: 13 }}>
          Deterministic patch proposals generated from editable blocks and pre-validated on the backend.
        </span>
      </div>
      {visibleProposals.length === 0 ? (
        <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
          No mocked patch proposals are available for the current draft.
        </p>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {visibleProposals.map((proposal) => (
            <div key={proposal.id} style={proposalCardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                <strong style={{ fontSize: 14 }}>{proposal.label}</strong>
                <span style={badgeStyle}>validated</span>
              </div>
              <span style={{ color: "#9ba3b4", fontSize: 12 }}>
                Lines {proposal.startLine}-{proposal.endLine}
              </span>
              <div style={diffBlockStyle}>
                <div style={removedStyle}>
                  <span style={diffLabelStyle}>Before</span>
                  <p style={diffTextStyle}>{proposal.beforeText}</p>
                </div>
                <div style={addedStyle}>
                  <span style={diffLabelStyle}>After</span>
                  <p style={diffTextStyle}>{proposal.afterText}</p>
                </div>
              </div>
              <p style={rationaleStyle}>{proposal.rationale}</p>
              <div style={actionsStyle}>
                <button
                  disabled={applyingId !== null}
                  onClick={() => void handleApply(proposal)}
                  style={primaryButtonStyle}
                  type="button"
                >
                  {applyingId === proposal.id ? "Applying..." : "Apply"}
                </button>
                <button
                  disabled={applyingId !== null}
                  onClick={() => setDismissedIds((current) => [...current, proposal.id])}
                  style={secondaryButtonStyle}
                  type="button"
                >
                  Dismiss
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
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

const proposalCardStyle: CSSProperties = {
  display: "grid",
  gap: 10,
  padding: 12,
  border: "1px solid #262b36",
  borderRadius: 12,
  background: "#171a21",
};

const badgeStyle: CSSProperties = {
  padding: "2px 8px",
  borderRadius: 999,
  background: "#183424",
  color: "#b5f0c9",
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
};

const diffBlockStyle: CSSProperties = {
  display: "grid",
  gap: 8,
};

const removedStyle: CSSProperties = {
  display: "grid",
  gap: 4,
  padding: 10,
  borderRadius: 10,
  background: "#2a1417",
};

const addedStyle: CSSProperties = {
  display: "grid",
  gap: 4,
  padding: 10,
  borderRadius: 10,
  background: "#13261a",
};

const diffLabelStyle: CSSProperties = {
  color: "#9ba3b4",
  fontSize: 11,
  textTransform: "uppercase",
  letterSpacing: "0.06em",
};

const diffTextStyle: CSSProperties = {
  margin: 0,
  color: "#eef1f6",
  fontSize: 13,
  lineHeight: 1.5,
};

const rationaleStyle: CSSProperties = {
  margin: 0,
  color: "#9ba3b4",
  fontSize: 12,
  lineHeight: 1.5,
};

const actionsStyle: CSSProperties = {
  display: "flex",
  gap: 8,
};

const primaryButtonStyle: CSSProperties = {
  padding: "8px 12px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#eef1f6",
  color: "#0f1115",
  cursor: "pointer",
};

const secondaryButtonStyle: CSSProperties = {
  ...primaryButtonStyle,
  background: "#171a21",
  color: "#eef1f6",
};
