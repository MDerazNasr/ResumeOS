"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import type { MockPatchProposalDto, MockSuggestionSetDto } from "@/lib/api/types";

type SuggestionReviewPanelProps = {
  onRetrySet: (suggestionSet: MockSuggestionSetDto) => Promise<void>;
  onApply: (proposal: MockPatchProposalDto) => Promise<boolean>;
  suggestionSets: MockSuggestionSetDto[];
};

export function SuggestionReviewPanel({ onApply, onRetrySet, suggestionSets }: SuggestionReviewPanelProps) {
  const [dismissedIds, setDismissedIds] = useState<string[]>([]);
  const [applyingId, setApplyingId] = useState<string | null>(null);
  const [retryingSetId, setRetryingSetId] = useState<string | null>(null);
  const visibleSuggestionSets = suggestionSets
    .map((suggestionSet) => ({
      ...suggestionSet,
      items: suggestionSet.items.filter((proposal) => !dismissedIds.includes(proposal.id)),
    }))
    .filter((suggestionSet) => suggestionSet.items.length > 0);

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

  async function handleRetrySet(suggestionSet: MockSuggestionSetDto) {
    setRetryingSetId(suggestionSet.id);

    try {
      await onRetrySet(suggestionSet);
      setDismissedIds([]);
    } finally {
      setRetryingSetId(null);
    }
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Suggestions</strong>
        <span style={{ color: "#9ba3b4", fontSize: 13 }}>
          Structured suggestion sets rendered as validated patch hunks against the current draft.
        </span>
      </div>
      {visibleSuggestionSets.length === 0 ? (
        <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
          No suggestions are available for the current draft.
        </p>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {visibleSuggestionSets.map((suggestionSet) => (
            <div key={suggestionSet.id} style={setCardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start" }}>
                <div style={{ display: "grid", gap: 6 }}>
                  <strong style={{ fontSize: 15 }}>{suggestionSet.title}</strong>
                  <p style={setSummaryStyle}>{suggestionSet.summary}</p>
                </div>
                <button
                  disabled={retryingSetId !== null || applyingId !== null}
                  onClick={() => void handleRetrySet(suggestionSet)}
                  style={secondaryButtonStyle}
                  type="button"
                >
                  {retryingSetId === suggestionSet.id ? "Retrying..." : "Regenerate"}
                </button>
              </div>
              <div style={{ display: "grid", gap: 12 }}>
                {suggestionSet.items.map((proposal) => (
                  <div key={proposal.id} style={proposalCardStyle}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start" }}>
                      <div style={{ display: "grid", gap: 4 }}>
                        <strong style={{ fontSize: 14 }}>{proposal.label}</strong>
                        <span style={{ color: "#9ba3b4", fontSize: 12 }}>
                          {proposal.operation} • lines {proposal.startLine}-{proposal.endLine}
                        </span>
                      </div>
                      <span style={badgeStyle}>{proposal.status}</span>
                    </div>
                    <div style={diffHunkStyle}>
                      <div style={diffLineStyle("removed")}>
                        <span style={lineMarkerStyle("removed")}>-</span>
                        <code style={diffCodeStyle}>{proposal.beforeText}</code>
                      </div>
                      <div style={diffLineStyle("added")}>
                        <span style={lineMarkerStyle("added")}>+</span>
                        <code style={diffCodeStyle}>{proposal.afterText}</code>
                      </div>
                    </div>
                    <p style={rationaleStyle}>{proposal.rationale}</p>
                    <div style={actionsStyle}>
                      <button
                        disabled={applyingId !== null || retryingSetId !== null}
                        onClick={() => void handleApply(proposal)}
                        style={primaryButtonStyle}
                        type="button"
                      >
                        {applyingId === proposal.id ? "Applying..." : "Apply"}
                      </button>
                      <button
                        disabled={applyingId !== null || retryingSetId !== null}
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

const setCardStyle: CSSProperties = {
  display: "grid",
  gap: 14,
  padding: 14,
  border: "1px solid #313748",
  borderRadius: 14,
  background: "#151922",
};

const setSummaryStyle: CSSProperties = {
  margin: 0,
  color: "#9ba3b4",
  fontSize: 13,
  lineHeight: 1.5,
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

const diffHunkStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  border: "1px solid #262b36",
  borderRadius: 12,
  overflow: "hidden",
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

function diffLineStyle(type: "added" | "removed"): CSSProperties {
  return {
    display: "grid",
    gridTemplateColumns: "18px minmax(0, 1fr)",
    gap: 10,
    padding: "10px 12px",
    background: type === "added" ? "#13261a" : "#2a1417",
    alignItems: "start",
  };
}

function lineMarkerStyle(type: "added" | "removed"): CSSProperties {
  return {
    color: type === "added" ? "#8ae6a3" : "#ff9b9b",
    fontWeight: 700,
    fontFamily: "var(--font-geist-mono, monospace)",
    fontSize: 13,
    paddingTop: 1,
  };
}

const diffCodeStyle: CSSProperties = {
  color: "#eef1f6",
  fontSize: 12,
  lineHeight: 1.6,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  fontFamily: "var(--font-geist-mono, monospace)",
};
