"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import type { MockPatchProposalDto, MockSuggestionSetDto } from "@/lib/api/types";

type SuggestionReviewPanelProps = {
  onRetrySet: (suggestionSet: MockSuggestionSetDto) => Promise<void>;
  onApply: (suggestionSet: MockSuggestionSetDto, proposal: MockPatchProposalDto) => Promise<boolean>;
  onDismiss: (suggestionSet: MockSuggestionSetDto, proposal: MockPatchProposalDto) => Promise<boolean>;
  isLoading?: boolean;
  emptyMessage?: string | null;
  suggestionSets: MockSuggestionSetDto[];
};

export function SuggestionReviewPanel({
  onApply,
  onDismiss,
  onRetrySet,
  suggestionSets,
  isLoading = false,
  emptyMessage = null,
}: SuggestionReviewPanelProps) {
  const [dismissedIds, setDismissedIds] = useState<string[]>([]);
  const [applyingId, setApplyingId] = useState<string | null>(null);
  const [dismissingId, setDismissingId] = useState<string | null>(null);
  const [retryingSetId, setRetryingSetId] = useState<string | null>(null);
  const visibleSuggestionSets = suggestionSets
    .map((suggestionSet) => ({
      ...suggestionSet,
      items: suggestionSet.items.filter((proposal) => !dismissedIds.includes(proposal.id)),
    }))
    .filter((suggestionSet) => suggestionSet.items.length > 0);

  async function handleApply(suggestionSet: MockSuggestionSetDto, proposal: MockPatchProposalDto) {
    setApplyingId(proposal.id);

    try {
      const applied = await onApply(suggestionSet, proposal);
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

  async function handleDismiss(suggestionSet: MockSuggestionSetDto, proposal: MockPatchProposalDto) {
    setDismissingId(proposal.id);

    try {
      const dismissed = await onDismiss(suggestionSet, proposal);
      if (dismissed) {
        setDismissedIds((current) => [...current, proposal.id]);
      }
    } finally {
      setDismissingId(null);
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
      {isLoading ? (
        <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
          Generating suggestions for the current draft...
        </p>
      ) : visibleSuggestionSets.length === 0 && suggestionSets.length > 0 ? (
        <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
          All current suggestions were dismissed. Regenerate a set to try again.
        </p>
      ) : visibleSuggestionSets.length === 0 ? (
        <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
          {emptyMessage ?? "No suggestions are available for the current draft."}
        </p>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {visibleSuggestionSets.map((suggestionSet) => (
            <div key={suggestionSet.id} style={setCardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start" }}>
                <div style={{ display: "grid", gap: 6 }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  <strong style={{ fontSize: 15 }}>{suggestionSet.title}</strong>
                    <span style={modeBadgeStyle(suggestionSet.mode)}>{suggestionSet.mode}</span>
                  </div>
                  <p style={setSummaryStyle}>{suggestionSet.summary}</p>
                </div>
                <button
                  disabled={retryingSetId !== null || applyingId !== null || dismissingId !== null}
                  onClick={() => void handleRetrySet(suggestionSet)}
                  style={secondaryButtonStyle}
                  type="button"
                >
                  {retryingSetId === suggestionSet.id ? retryLabel(suggestionSet.mode, true) : retryLabel(suggestionSet.mode, false)}
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
                        disabled={applyingId !== null || retryingSetId !== null || dismissingId !== null}
                        onClick={() => void handleApply(suggestionSet, proposal)}
                        style={primaryButtonStyle}
                        type="button"
                      >
                        {applyingId === proposal.id ? "Applying..." : "Apply"}
                      </button>
                      <button
                        disabled={applyingId !== null || retryingSetId !== null || dismissingId !== null}
                        onClick={() => void handleDismiss(suggestionSet, proposal)}
                        style={secondaryButtonStyle}
                        type="button"
                      >
                        {dismissingId === proposal.id ? "Dismissing..." : "Dismiss"}
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

function modeBadgeStyle(mode: MockSuggestionSetDto["mode"]): CSSProperties {
  const palette =
    mode === "tailor"
      ? { background: "#2b1f12", color: "#ffd7a3" }
      : mode === "review"
        ? { background: "#142434", color: "#b8dcff" }
        : mode === "edit"
          ? { background: "#1f1f33", color: "#d8d0ff" }
          : { background: "#243127", color: "#b5f0c9" };

  return {
    ...badgeStyle,
    background: palette.background,
    color: palette.color,
  };
}

function retryLabel(mode: MockSuggestionSetDto["mode"], isLoading: boolean): string {
  if (isLoading) {
    return mode === "tailor" ? "Retailoring..." : mode === "review" ? "Rereviewing..." : mode === "edit" ? "Regenerating edit..." : "Retrying...";
  }

  return mode === "tailor" ? "Retailor" : mode === "review" ? "Rereview" : mode === "edit" ? "Regenerate Edit" : "Regenerate";
}

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
