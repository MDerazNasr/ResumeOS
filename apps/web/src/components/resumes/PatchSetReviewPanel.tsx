"use client";

import { useEffect, useMemo, useState } from "react";
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
  const [activeHunkId, setActiveHunkId] = useState<string | null>(null);
  const [isApplyingAll, setIsApplyingAll] = useState(false);
  const [isRejectingAll, setIsRejectingAll] = useState(false);
  const [completionMessage, setCompletionMessage] = useState<string | null>(null);

  const visiblePatchSets = useMemo(
    () =>
      patchSets
        .map((patchSet) => ({
          ...patchSet,
          items: patchSet.items.filter((hunk) => !dismissedIds.includes(hunk.id)),
        }))
        .filter((patchSet) => patchSet.items.length > 0),
    [dismissedIds, patchSets],
  );

  const visibleHunks = useMemo(
    () =>
      visiblePatchSets.flatMap((patchSet) =>
        patchSet.items.map((hunk) => ({
          patchSet,
          hunk,
        })),
      ),
    [visiblePatchSets],
  );

  const activeHunkIndex = visibleHunks.findIndex(({ hunk }) => hunk.id === activeHunkId);
  const activeHunkCountLabel =
    visibleHunks.length === 0 || activeHunkIndex === -1 ? "No active hunk" : `Hunk ${activeHunkIndex + 1} of ${visibleHunks.length}`;

  useEffect(() => {
    if (visibleHunks.length === 0) {
      setActiveHunkId(null);
      return;
    }

    if (!activeHunkId || !visibleHunks.some(({ hunk }) => hunk.id === activeHunkId)) {
      setActiveHunkId(visibleHunks[0]?.hunk.id ?? null);
    }
  }, [activeHunkId, visibleHunks]);

  useEffect(() => {
    if (visibleHunks.length > 0) {
      setCompletionMessage(null);
    }
  }, [visibleHunks.length]);

  function dismissHunkFromView(hunkId: string) {
    setDismissedIds((current) => [...current, hunkId]);
  }

  function setNextActiveHunk(removedHunkId: string) {
    const currentIndex = visibleHunks.findIndex(({ hunk }) => hunk.id === removedHunkId);
    const remainingHunks = visibleHunks.filter(({ hunk }) => hunk.id !== removedHunkId);

    if (remainingHunks.length === 0) {
      setActiveHunkId(null);
      return;
    }

    const nextIndex = currentIndex === -1 ? 0 : Math.min(currentIndex, remainingHunks.length - 1);
    setActiveHunkId(remainingHunks[nextIndex]?.hunk.id ?? null);
  }

  async function handleApply(patchSet: PatchSetDto, hunk: PatchHunkDto) {
    setApplyingId(hunk.id);

    try {
      const applied = await onApply(patchSet, hunk);
      if (applied) {
        setNextActiveHunk(hunk.id);
        dismissHunkFromView(hunk.id);
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
      setCompletionMessage(null);
    } finally {
      setRetryingSetId(null);
    }
  }

  async function handleDismiss(patchSet: PatchSetDto, hunk: PatchHunkDto) {
    setDismissingId(hunk.id);

    try {
      const dismissed = await onDismiss(patchSet, hunk);
      if (dismissed) {
        setNextActiveHunk(hunk.id);
        dismissHunkFromView(hunk.id);
      }
    } finally {
      setDismissingId(null);
    }
  }

  async function handleApplyAll() {
    if (visibleHunks.length === 0) {
      return;
    }

    setIsApplyingAll(true);

    try {
      for (const { patchSet, hunk } of visibleHunks) {
        const applied = await onApply(patchSet, hunk);
        if (!applied) {
          break;
        }

        dismissHunkFromView(hunk.id);
      }
      setActiveHunkId(null);
      setCompletionMessage("All visible hunks were approved.");
    } finally {
      setIsApplyingAll(false);
    }
  }

  async function handleRejectAll() {
    if (visibleHunks.length === 0) {
      return;
    }

    setIsRejectingAll(true);

    try {
      for (const { patchSet, hunk } of visibleHunks) {
        const dismissed = await onDismiss(patchSet, hunk);
        if (dismissed) {
          dismissHunkFromView(hunk.id);
        }
      }
      setActiveHunkId(null);
      setCompletionMessage("All visible hunks were rejected.");
    } finally {
      setIsRejectingAll(false);
    }
  }

  function moveActiveHunk(direction: "previous" | "next") {
    if (visibleHunks.length === 0) {
      return;
    }

    const currentIndex = activeHunkIndex === -1 ? 0 : activeHunkIndex;
    const nextIndex =
      direction === "previous"
        ? Math.max(0, currentIndex - 1)
        : Math.min(visibleHunks.length - 1, currentIndex + 1);

    setActiveHunkId(visibleHunks[nextIndex]?.hunk.id ?? null);
  }

  const hasBusyAction =
    applyingId !== null ||
    dismissingId !== null ||
    retryingSetId !== null ||
    isApplyingAll ||
    isRejectingAll;

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Patch Sets</strong>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>
          Review AI changes like a code diff before they touch the draft.
        </span>
      </div>
      {completionMessage ? <p style={completionMessageStyle}>{completionMessage}</p> : null}
      {visibleHunks.length > 0 ? (
        <div style={reviewToolbarStyle}>
          <div style={{ display: "grid", gap: 4 }}>
            <strong style={{ fontSize: 13 }}>Review Controls</strong>
            <span style={{ color: "var(--muted)", fontSize: 12 }}>{activeHunkCountLabel}</span>
          </div>
          <div style={toolbarActionsStyle}>
            <button
              disabled={hasBusyAction || activeHunkIndex <= 0}
              onClick={() => moveActiveHunk("previous")}
              style={secondaryButtonStyle}
              type="button"
            >
              Previous
            </button>
            <button
              disabled={hasBusyAction || activeHunkIndex === -1 || activeHunkIndex >= visibleHunks.length - 1}
              onClick={() => moveActiveHunk("next")}
              style={secondaryButtonStyle}
              type="button"
            >
              Next
            </button>
            <button
              disabled={hasBusyAction || visibleHunks.length === 0}
              onClick={() => void handleApplyAll()}
              style={primaryButtonStyle}
              type="button"
            >
              {isApplyingAll ? "Approving..." : "Approve All"}
            </button>
            <button
              disabled={hasBusyAction || visibleHunks.length === 0}
              onClick={() => void handleRejectAll()}
              style={secondaryButtonStyle}
              type="button"
            >
              {isRejectingAll ? "Rejecting..." : "Reject All"}
            </button>
          </div>
        </div>
      ) : null}
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
                  <span style={setMetaStyle}>
                    {patchSet.items.length} visible {patchSet.items.length === 1 ? "hunk" : "hunks"}
                  </span>
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
                  <div
                    key={hunk.id}
                    onClick={() => setActiveHunkId(hunk.id)}
                    style={proposalCardStyle(hunk.id === activeHunkId)}
                  >
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
                      <div style={diffHeaderStyle}>
                        <span style={{ color: "var(--muted)" }}>Review Hunk</span>
                        <span style={{ color: "var(--muted)" }}>
                          {hunk.startLine === hunk.endLine ? `Line ${hunk.startLine}` : `Lines ${hunk.startLine}-${hunk.endLine}`}
                        </span>
                      </div>
                      {renderDiffLines("removed", hunk.beforeText)}
                      {renderDiffLines("added", hunk.afterText)}
                    </div>
                    <p style={rationaleStyle}>{hunk.rationale}</p>
                    <div style={actionsStyle}>
                      <button
                        disabled={hasBusyAction}
                        onClick={() => void handleApply(patchSet, hunk)}
                        style={primaryButtonStyle}
                        type="button"
                      >
                        {applyingId === hunk.id ? "Approving..." : "Approve"}
                      </button>
                      <button
                        disabled={hasBusyAction}
                        onClick={() => void handleDismiss(patchSet, hunk)}
                        style={secondaryButtonStyle}
                        type="button"
                      >
                        {dismissingId === hunk.id ? "Rejecting..." : "Reject"}
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

function proposalCardStyle(isActive: boolean): CSSProperties {
  return {
    display: "grid",
    gap: 10,
    padding: 12,
    border: `1px solid ${isActive ? "var(--mode-review-fg)" : "var(--border)"}`,
    borderRadius: 12,
    background: isActive ? "var(--surface-elevated)" : "var(--surface)",
    boxShadow: isActive ? "0 0 0 1px var(--mode-review-fg) inset" : "none",
    cursor: "pointer",
  };
}

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

const setMetaStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 12,
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
  gap: 0,
  border: "1px solid var(--border)",
  borderRadius: 12,
  overflow: "hidden",
  background: "var(--surface-elevated)",
};

const diffHeaderStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12,
  padding: "10px 12px",
  borderBottom: "1px solid var(--border)",
  background: "var(--surface)",
  fontSize: 11,
  fontWeight: 700,
  letterSpacing: "0.06em",
  textTransform: "uppercase",
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
  flexWrap: "wrap",
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

const reviewToolbarStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 16,
  alignItems: "center",
  padding: "12px 14px",
  border: "1px solid var(--border)",
  borderRadius: 14,
  background: "var(--surface)",
};

const toolbarActionsStyle: CSSProperties = {
  display: "flex",
  gap: 8,
  flexWrap: "wrap",
  justifyContent: "flex-end",
};

const completionMessageStyle: CSSProperties = {
  margin: 0,
  padding: "10px 12px",
  border: "1px solid var(--border)",
  borderRadius: 12,
  background: "var(--mode-mock-bg)",
  color: "var(--fg)",
  fontSize: 13,
  lineHeight: 1.5,
};

function diffLineStyle(type: "added" | "removed", isFirst: boolean): CSSProperties {
  return {
    display: "grid",
    gridTemplateColumns: "18px 48px minmax(0, 1fr)",
    gap: 10,
    padding: "10px 12px",
    background: type === "added" ? "var(--diff-add-bg)" : "var(--diff-remove-bg)",
    alignItems: "start",
    borderTop: isFirst ? "none" : "1px solid var(--border)",
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

const lineNumberStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 12,
  fontFamily: "var(--font-geist-mono, monospace)",
  textAlign: "right",
  paddingTop: 1,
};

const diffCodeStyle: CSSProperties = {
  color: "var(--fg)",
  fontSize: 12,
  lineHeight: 1.6,
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  fontFamily: "var(--font-geist-mono, monospace)",
};

function renderDiffLines(type: "added" | "removed", text: string) {
  const lines = text.split("\n");

  return lines.map((line, index) => (
    <div key={`${type}-${index}-${line}`} style={diffLineStyle(type, index === 0)}>
      <span style={lineMarkerStyle(type)}>{type === "added" ? "+" : "-"}</span>
      <span style={lineNumberStyle}>{index + 1}</span>
      <code style={diffCodeStyle}>{line || " "}</code>
    </div>
  ));
}
