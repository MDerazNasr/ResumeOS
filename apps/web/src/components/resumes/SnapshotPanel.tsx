"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import { createSnapshot, getSnapshot, restoreSnapshot } from "@/lib/api/client";
import { SnapshotCompareView } from "@/components/resumes/SnapshotCompareView";
import type { SnapshotDetailDto, SnapshotDto, WorkingDraftDto } from "@/lib/api/types";

type SnapshotPanelProps = {
  currentSourceTex: string;
  ensureLatestDraft: () => Promise<boolean>;
  initialSnapshots: SnapshotDto[];
  resumeId: string;
  onRestore: (draft: WorkingDraftDto) => void;
};

export function SnapshotPanel({
  currentSourceTex,
  ensureLatestDraft,
  initialSnapshots,
  resumeId,
  onRestore,
}: SnapshotPanelProps) {
  const [snapshots, setSnapshots] = useState(initialSnapshots);
  const [snapshotName, setSnapshotName] = useState("Manual Snapshot");
  const [isSavingSnapshot, setIsSavingSnapshot] = useState(false);
  const [isRestoringSnapshot, setIsRestoringSnapshot] = useState<string | null>(null);
  const [isLoadingCompare, setIsLoadingCompare] = useState<string | null>(null);
  const [compareSnapshot, setCompareSnapshot] = useState<SnapshotDetailDto | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function handleCreateSnapshot(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSavingSnapshot(true);
    setError(null);
    setMessage(null);

    try {
      const draftReady = await ensureLatestDraft();
      if (!draftReady) {
        return;
      }

      const snapshot = await createSnapshot(resumeId, { name: snapshotName });
      setSnapshots((current) => [snapshot, ...current]);
      setSnapshotName(`Snapshot ${snapshots.length + 2}`);
      setMessage(`Snapshot "${snapshot.name}" created.`);
    } catch (snapshotError) {
      setError(snapshotError instanceof Error ? snapshotError.message : "Failed to create snapshot.");
    } finally {
      setIsSavingSnapshot(false);
    }
  }

  async function handleRestoreSnapshot(snapshotId: string) {
    const snapshot = snapshots.find((item) => item.id === snapshotId);
    const confirmed = window.confirm(
      `Restore "${snapshot?.name ?? "this snapshot"}"? This will replace the current working draft.`
    );

    if (!confirmed) {
      return;
    }

    setIsRestoringSnapshot(snapshotId);
    setError(null);
    setMessage(null);

    try {
      const restoredDraft = await restoreSnapshot(resumeId, { snapshotId });
      onRestore(restoredDraft);
      setMessage(`Restored "${snapshot?.name ?? "snapshot"}" into the working draft.`);
    } catch (restoreError) {
      setError(restoreError instanceof Error ? restoreError.message : "Failed to restore snapshot.");
    } finally {
      setIsRestoringSnapshot(null);
    }
  }

  async function handleCompareSnapshot(snapshotId: string) {
    setIsLoadingCompare(snapshotId);
    setError(null);
    setMessage(null);

    try {
      const snapshot = await getSnapshot(resumeId, snapshotId);
      setCompareSnapshot(snapshot);
    } catch (compareError) {
      setError(compareError instanceof Error ? compareError.message : "Failed to load snapshot comparison.");
    } finally {
      setIsLoadingCompare(null);
    }
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Snapshots</strong>
        <span style={{ color: "#9ba3b4", fontSize: 13 }}>Save named versions of the current working draft.</span>
      </div>
      <form onSubmit={handleCreateSnapshot} style={formStyle}>
        <input
          onChange={(event) => setSnapshotName(event.target.value)}
          placeholder="Manual Snapshot"
          style={inputStyle}
          value={snapshotName}
        />
        <button disabled={isSavingSnapshot || snapshotName.trim().length === 0} style={buttonStyle} type="submit">
          {isSavingSnapshot ? "Saving..." : "Create Snapshot"}
        </button>
      </form>
      <div style={listStyle}>
        {snapshots.length === 0 ? (
          <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>No snapshots yet.</p>
        ) : (
          snapshots.map((snapshot) => (
            <div key={snapshot.id} style={snapshotItemStyle}>
              <div style={{ display: "grid", gap: 4 }}>
                <strong style={{ fontSize: 14 }}>{snapshot.name}</strong>
                <span style={{ color: "#9ba3b4", fontSize: 12 }}>
                  v{snapshot.sourceVersion} • {new Date(snapshot.createdAt).toLocaleString()}
                </span>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button
                  disabled={isLoadingCompare !== null || isRestoringSnapshot !== null}
                  onClick={() => handleCompareSnapshot(snapshot.id)}
                  style={secondaryButtonStyle}
                  type="button"
                >
                  {isLoadingCompare === snapshot.id ? "Loading..." : "Compare"}
                </button>
                <button
                  disabled={isRestoringSnapshot !== null || isLoadingCompare !== null}
                  onClick={() => handleRestoreSnapshot(snapshot.id)}
                  style={secondaryButtonStyle}
                  type="button"
                >
                  {isRestoringSnapshot === snapshot.id ? "Restoring..." : "Restore"}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
      {compareSnapshot ? (
        <SnapshotCompareView
          currentSource={currentSourceTex}
          onClose={() => setCompareSnapshot(null)}
          snapshotName={compareSnapshot.name}
          snapshotSource={compareSnapshot.sourceTex}
        />
      ) : null}
      {error ? <p style={errorStyle}>{error}</p> : null}
      {message ? <p style={messageStyle}>{message}</p> : null}
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

const formStyle: CSSProperties = {
  display: "grid",
  gap: 10,
};

const inputStyle: CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  border: "1px solid #313748",
  borderRadius: 12,
  background: "#0f1115",
  color: "#eef1f6",
};

const buttonStyle: CSSProperties = {
  width: "fit-content",
  padding: "10px 14px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#eef1f6",
  color: "#0f1115",
  cursor: "pointer",
};

const secondaryButtonStyle: CSSProperties = {
  ...buttonStyle,
  background: "#171a21",
  color: "#eef1f6",
};

const listStyle: CSSProperties = {
  display: "grid",
  gap: 10,
};

const snapshotItemStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 16,
  alignItems: "center",
  padding: 12,
  border: "1px solid #262b36",
  borderRadius: 12,
  background: "#171a21",
};

const errorStyle: CSSProperties = {
  margin: 0,
  color: "#ff8d8d",
};

const messageStyle: CSSProperties = {
  margin: 0,
  color: "#9fe0b0",
};
