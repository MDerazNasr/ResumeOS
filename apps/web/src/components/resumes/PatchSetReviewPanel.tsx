"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import type { PatchHunkDto, PatchSetDto } from "@/lib/api/types";

type PatchSetReviewPanelProps = {
  onRetrySet: (patchSet: PatchSetDto) => Promise<void>;
  onApply: (patchSet: PatchSetDto, hunk: PatchHunkDto) => Promise<boolean>;
  onDismiss: (patchSet: PatchSetDto, hunk: PatchHunkDto) => Promise<boolean>;
  isLoading?: boolean;
  emptyMessage?: string | null;
  patchSets: PatchSetDto[];
};

export function PatchSetReviewPanel({
  onApply,
  onDismiss,
  onRetrySet,
  patchSets,
  isLoading = false,
  emptyMessage = null,
}: PatchSetReviewPanelProps) {
  const [dismissedIds, setDismissedIds] = useState<string[]>([]);
  const [applyingId, setApplyingId] = useState<string | null>(null);
  const [dismissingId, setDismissingId] = useState<string | null>(null);
  const [retryingSetId, setRetryingSetId] = useState<string | null>(null);
  const visiblePatchSets = patchSets
    .map((patchSet) => ({
      ...patchSet,
      items: patchSet.items.filter((hunk) => !dismissedIds.includes(hunk.id)),
    }))
    .filter((patchSet) => patchSet.items.length > 0);

  async function handleApply(patchSet: PatchSetDto, hunk: PatchHunkDto) {
    setApplyingId(hunk.id);

    try {
      const applied = await onApply(patchSet, hunk);
      if (applied) {
        setDismissedIds((current) => [...current, hunk.id]);
      }
    } finally {
      setApplyingId(null);
    }
  }

  async function handleRetrySet(patchSet: PatchSetDto) {
    setRetryingSetId(patchSet.id);

    try {
      await onRetrySet(patchSet);
      setDismissedIds([]);
    } finally {
      setRetryingSetId(null);
    }
  }

  async function handleDismiss(patchSet: PatchSetDto, hunk: PatchHunkDto) {
    setDismissingId(hunk.id);

    try {
      const dismissed = await onDismiss(patchSet, hunk);
      if (dismissed) {
        setDismissedIds((current) => [...current, hunk.id]);
      }
    } finally {
      setDismissingId(null);
    }
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Patch Sets</strong>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>
          Structured patch sets rendered as validated hunks against the current draft.
        </span>
      </div>
      {isLoading ? (
        <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.6 }}>
          Generating patch sets for the current draft...
        </p>
      ) : visiblePatchSets.length === 0 && patchSets.length > 0 ? (
        <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.6 }}>
          All current patch hunks were dismissed. Regenerate a patch set to try again.
        </p>
      ) : visiblePatchSets.length === 0 ? (
        <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.6 }}>
          {emptyMessage ?? "No patch sets are available for the current draft."}
        </p>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {visiblePatchSets.map((patchSet) => (
            <div key={patchSet.id} style={setCardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start" }}>
                <div style={{ display: "grid", gap: 6 }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                    <strong style={{ fontSize: 15 }}>{patchSet.title}</strong>
                    <span style={modeBadgeStyle(patchSet.mode)}>{patchSet.mode}</span>
                  </div>
                  <p style={setSummaryStyle}>{patchSet.summary}</p>
                  {patchSet.styleExamples.length > 0 ? (
                    <div style={styleExamplesStyle}>
                      <span style={styleExamplesLabelStyle}>Style memory</span>
                      <div style={{ display: "grid", gap: 6 }}>
                        {patchSet.styleExamples.map((example) => (
                          <code key={example} style={styleExampleCodeStyle}>
                            {example}
                          </code>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
                <button
                  disabled={retryingSetId !== null || applyingId !== null || dismissingId !== null}
                  onClick={() => void handleRetrySet(patchSet)}
                  style={secondaryButtonStyle}
                  type="button"
                >
                  {retryingSetId === patchSet.id ? retryLabel(patchSet.mode, true) : retryLabel(patchSet.mode, false)}
                </button>
              </div>
              <div style={{ display: "grid", gap: 12 }}>
                {patchSet.items.map((hunk) => (
                  <div key={hunk.id} style={proposalCardStyle}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "start" }}>
                      <div style={{ display: "grid", gap: 4 }}>
                        <strong style={{ fontSize: 14 }}>{hunk.label}</strong>
                        <span style={{ color: "var(--muted)", fontSize: 12 }}>
                          {hunk.operation} • lines {hunk.startLine}-{hunk.endLine}
                        </span>
                      </div>
                      <span style={badgeStyle}>{hunk.status}</span>
                    </div>
                    <div style={diffHunkStyle}>
                      <div style={diffLineStyle("removed")}>
                        <span style={lineMarkerStyle("removed")}>-</span>
                        <code style={diffCodeStyle}>{hunk.beforeText}</code>
                      </div>
                      <div style={diffLineStyle("added")}>
                        <span style={lineMarkerStyle("added")}>+</span>
                        <code style={diffCodeStyle}>{hunk.afterText}</code>
                      </div>
                    </div>
                    <p style={rationaleStyle}>{hunk.rationale}</p>
                    <div style={actionsStyle}>
                      <button
                        disabled={applyingId !== null || retryingSetId !== null || dismissingId !== null}
                        onClick={() => void handleApply(patchSet, hunk)}
                        style={primaryButtonStyle}
                        type="button"
                      >
                        {applyingId === hunk.id ? "Applying..." : "Apply"}
                      </button>
                      <button
                        disabled={applyingId !== null || retryingSetId !== null || dismissingId !== null}
                        onClick={() => void handleDismiss(patchSet, hunk)}
                        style={secondaryButtonStyle}
                        type="button"
                      >
                        {dismissingId === hunk.id ? "Dismissing..." : "Dismiss"}
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
  border: "1px solid var(--border)",
  borderRadius: 16,
  background: "var(--surface-alt)",
};

const proposalCardStyle: CSSProperties = {
  display: "grid",
  gap: 10,
  padding: 12,
  border: "1px solid var(--border)",
  borderRadius: 12,
  background: "var(--surface)",
};

const setCardStyle: CSSProperties = {
  display: "grid",
  gap: 14,
  padding: 14,
  border: "1px solid var(--border-strong)",
  borderRadius: 14,
  background: "var(--surface-elevated)",
};

const setSummaryStyle: CSSProperties = {
  margin: 0,
  color: "var(--muted)",
  fontSize: 13,
  lineHeight: 1.5,
};

const styleExamplesStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  padding: 10,
  border: "1px solid var(--border)",
  borderRadius: 12,
  background: "var(--style-memory-bg)",
};

const styleExamplesLabelStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 11,
  fontWeight: 700,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
};

const styleExampleCodeStyle: CSSProperties = {
  color: "var(--fg)",
  fontSize: 12,
  lineHeight: 1.5,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  fontFamily: "var(--font-geist-mono, monospace)",
};

const badgeStyle: CSSProperties = {
  padding: "2px 8px",
  borderRadius: 999,
  background: "var(--mode-mock-bg)",
  color: "var(--mode-mock-fg)",
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
};

function modeBadgeStyle(mode: PatchSetDto["mode"]): CSSProperties {
  const palette =
    mode === "tailor"
      ? { background: "var(--mode-tailor-bg)", color: "var(--mode-tailor-fg)" }
      : mode === "review"
        ? { background: "var(--mode-review-bg)", color: "var(--mode-review-fg)" }
        : mode === "edit"
          ? { background: "var(--mode-edit-bg)", color: "var(--mode-edit-fg)" }
          : { background: "var(--mode-mock-bg)", color: "var(--mode-mock-fg)" };

  return {
    ...badgeStyle,
    background: palette.background,
    color: palette.color,
  };
}

function retryLabel(mode: PatchSetDto["mode"], isLoading: boolean): string {
  if (isLoading) {
    return mode === "tailor" ? "Retailoring..." : mode === "review" ? "Rereviewing..." : mode === "edit" ? "Regenerating edit..." : "Retrying...";
  }

  return mode === "tailor" ? "Retailor" : mode === "review" ? "Rereview" : mode === "edit" ? "Regenerate Edit" : "Regenerate";
}

const diffHunkStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  border: "1px solid var(--border)",
  borderRadius: 12,
  overflow: "hidden",
};

const rationaleStyle: CSSProperties = {
  margin: 0,
  color: "var(--muted)",
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
  background: "var(--accent-bg)",
  color: "var(--accent-fg)",
  cursor: "pointer",
};

const secondaryButtonStyle: CSSProperties = {
  ...primaryButtonStyle,
  background: "var(--surface)",
  color: "var(--fg)",
};

function diffLineStyle(type: "added" | "removed"): CSSProperties {
  return {
    display: "grid",
    gridTemplateColumns: "18px minmax(0, 1fr)",
    gap: 10,
    padding: "10px 12px",
    background: type === "added" ? "var(--diff-add-bg)" : "var(--diff-remove-bg)",
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
  color: "var(--fg)",
  fontSize: 12,
  lineHeight: 1.6,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  fontFamily: "var(--font-geist-mono, monospace)",
};
