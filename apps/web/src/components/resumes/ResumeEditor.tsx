"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { compileDraft, getDocumentModel, saveDraft } from "@/lib/api/client";
import { DocumentModelPanel } from "@/components/resumes/DocumentModelPanel";
import { LatexEditor } from "@/components/resumes/LatexEditor";
import { SnapshotPanel } from "@/components/resumes/SnapshotPanel";
import type { CompileResultDto, DocumentModelDto, ResumeDto, SnapshotDto, WorkingDraftDto } from "@/lib/api/types";

type ResumeEditorProps = {
  documentModel: DocumentModelDto;
  draft: WorkingDraftDto;
  initialSnapshots: SnapshotDto[];
  resume: ResumeDto;
};

export function ResumeEditor({ documentModel, draft, initialSnapshots, resume }: ResumeEditorProps) {
  const [documentModelState, setDocumentModelState] = useState(documentModel);
  const [persistedSourceTex, setPersistedSourceTex] = useState(draft.sourceTex);
  const [sourceTex, setSourceTex] = useState(draft.sourceTex);
  const [version, setVersion] = useState(draft.version);
  const [updatedAt, setUpdatedAt] = useState(draft.updatedAt);
  const [isSaving, setIsSaving] = useState(false);
  const [isCompiling, setIsCompiling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compileResult, setCompileResult] = useState<CompileResultDto | null>(null);
  const [previewNonce, setPreviewNonce] = useState<number>(0);
  const saveInFlightRef = useRef<Promise<WorkingDraftDto | null> | null>(null);
  const sourceTexRef = useRef(sourceTex);
  const persistedSourceTexRef = useRef(persistedSourceTex);
  const versionRef = useRef(version);

  const isDirty = useMemo(() => sourceTex !== persistedSourceTex, [persistedSourceTex, sourceTex]);

  useEffect(() => {
    sourceTexRef.current = sourceTex;
  }, [sourceTex]);

  useEffect(() => {
    persistedSourceTexRef.current = persistedSourceTex;
  }, [persistedSourceTex]);

  useEffect(() => {
    versionRef.current = version;
  }, [version]);

  async function saveLatestDraft() {
    if (sourceTexRef.current === persistedSourceTexRef.current) {
      return null;
    }

    setIsSaving(true);
    setError(null);

    try {
      const savedDraft = await saveDraft(resume.id, {
        sourceTex: sourceTexRef.current,
        version: versionRef.current,
      });
      persistedSourceTexRef.current = savedDraft.sourceTex;
      versionRef.current = savedDraft.version;
      setPersistedSourceTex(savedDraft.sourceTex);
      setVersion(savedDraft.version);
      setUpdatedAt(savedDraft.updatedAt);
      const nextDocumentModel = await getDocumentModel(resume.id);
      setDocumentModelState(nextDocumentModel);
      return savedDraft;
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Failed to save draft.");
      return null;
    } finally {
      setIsSaving(false);
    }
  }

  async function ensureLatestDraftSaved() {
    if (saveInFlightRef.current) {
      await saveInFlightRef.current;
      if (sourceTexRef.current === persistedSourceTexRef.current) {
        return true;
      }
    }

    if (sourceTexRef.current === persistedSourceTexRef.current) {
      return true;
    }

    const savePromise = saveLatestDraft();
    saveInFlightRef.current = savePromise;

    try {
      const savedDraft = await savePromise;
      return sourceTexRef.current === persistedSourceTexRef.current || savedDraft !== null;
    } finally {
      if (saveInFlightRef.current === savePromise) {
        saveInFlightRef.current = null;
      }
    }
  }

  useEffect(() => {
    if (!isDirty) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      void ensureLatestDraftSaved();
    }, 800);

    return () => window.clearTimeout(timeoutId);
  }, [isDirty, sourceTex]);

  async function handleCompile() {
    setIsCompiling(true);
    setError(null);

    try {
      const draftReady = await ensureLatestDraftSaved();
      if (!draftReady) {
        return;
      }

      const result = await compileDraft(resume.id, {
        sourceTex: sourceTexRef.current,
        draftVersion: versionRef.current,
      });
      setCompileResult(result);
      setPreviewNonce(Date.now());
    } catch (compileError) {
      setError(compileError instanceof Error ? compileError.message : "Failed to compile draft.");
    } finally {
      setIsCompiling(false);
    }
  }

  function handleSnapshotRestore(restoredDraft: WorkingDraftDto) {
    setPersistedSourceTex(restoredDraft.sourceTex);
    setSourceTex(restoredDraft.sourceTex);
    setVersion(restoredDraft.version);
    setUpdatedAt(restoredDraft.updatedAt);
    setCompileResult(null);
    setError(null);
    void getDocumentModel(resume.id)
      .then((nextDocumentModel) => setDocumentModelState(nextDocumentModel))
      .catch(() => null);
  }

  return (
    <section style={shellStyle}>
      <div style={headerStyle}>
        <div style={{ display: "grid", gap: 4 }}>
          <h1 style={{ margin: 0, fontSize: 28 }}>{resume.title}</h1>
          <p style={{ margin: 0, color: "#9ba3b4" }}>Editor and compile workspace</p>
        </div>
        <div style={{ display: "grid", justifyItems: "end", gap: 8 }}>
          <div style={{ display: "flex", gap: 10 }}>
            <button disabled={isSaving || isCompiling} onClick={handleCompile} style={secondaryButtonStyle} type="button">
              {isCompiling ? "Compiling..." : "Compile"}
            </button>
          </div>
          <span style={{ color: isDirty ? "#f6d36e" : "#9ba3b4", fontSize: 13 }}>
            {isSaving
              ? "Saving..."
              : isDirty
                ? "Autosave pending..."
                : `Saved ${new Date(updatedAt).toLocaleString()}`}
          </span>
        </div>
      </div>
      <div style={workspaceStyle}>
        <LatexEditor onChange={setSourceTex} value={sourceTex} />
        <aside style={panelStyle}>
          <DocumentModelPanel documentModel={documentModelState} />
          <SnapshotPanel
            currentSourceTex={sourceTex}
            ensureLatestDraft={ensureLatestDraftSaved}
            initialSnapshots={initialSnapshots}
            onRestore={handleSnapshotRestore}
            resumeId={resume.id}
          />
          <div style={{ display: "grid", gap: 6 }}>
            <strong style={{ fontSize: 16 }}>Compile Panel</strong>
            <span style={{ color: "#9ba3b4", fontSize: 13 }}>
              {compileResult
                ? `Last compile ${new Date(compileResult.compiledAt).toLocaleString()}`
                : "No compile run yet"}
            </span>
          </div>
          <div style={statusCardStyle}>
            <span style={{ color: "#9ba3b4", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Status
            </span>
            <strong style={{ fontSize: 18 }}>
              {compileResult ? (compileResult.status === "success" ? "Success" : "Error") : "Idle"}
            </strong>
          </div>
          <div style={previewCardStyle}>
            <strong style={{ fontSize: 15 }}>Preview</strong>
            {compileResult?.pdfUrl ? (
              <iframe
                src={`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}${compileResult.pdfUrl}?t=${previewNonce}`}
                style={previewFrameStyle}
                title="Compiled PDF Preview"
              />
            ) : (
              <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
                Run a successful compile to render the latest generated PDF here.
              </p>
            )}
          </div>
          <div style={logsCardStyle}>
            <strong style={{ fontSize: 15 }}>Compile Logs</strong>
            <div style={{ display: "grid", gap: 10 }}>
              {compileResult ? (
                compileResult.logs.map((log, index) => (
                  <div key={`${log.level}-${index}`} style={logItemStyle(log.level)}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                      <span style={{ fontWeight: 600, textTransform: "uppercase", fontSize: 12 }}>{log.level}</span>
                      <span style={{ color: "#9ba3b4", fontSize: 12 }}>{log.line ? `Line ${log.line}` : "Global"}</span>
                    </div>
                    <span style={{ fontSize: 14, lineHeight: 1.5 }}>{log.message}</span>
                  </div>
                ))
              ) : (
                <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
                  Compile output will appear here after the first run.
                </p>
              )}
            </div>
          </div>
        </aside>
      </div>
      <div style={footerStyle}>
        <span style={{ color: "#9ba3b4", fontSize: 13 }}>Draft version {version}</span>
        {error ? <span style={{ color: "#ff8d8d", fontSize: 13 }}>{error}</span> : null}
      </div>
    </section>
  );
}

const shellStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  width: "100%",
  maxWidth: 1440,
  margin: "0 auto",
  padding: 32
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 24,
  alignItems: "flex-start"
};

const secondaryButtonStyle: CSSProperties = {
  padding: "10px 14px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#171a21",
  color: "#eef1f6",
  cursor: "pointer"
};

const workspaceStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "minmax(0, 1.65fr) minmax(320px, 0.85fr)",
  gap: 16,
  alignItems: "start"
};

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  padding: 20,
  border: "1px solid #262b36",
  borderRadius: 16,
  background: "#12151c"
};

const statusCardStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  padding: 16,
  border: "1px solid #262b36",
  borderRadius: 14,
  background: "#171a21"
};

const previewCardStyle: CSSProperties = {
  display: "grid",
  gap: 10,
  padding: 16,
  border: "1px solid #262b36",
  borderRadius: 14,
  background: "#171a21"
};

const previewFrameStyle: CSSProperties = {
  width: "100%",
  minHeight: 440,
  border: "1px solid #262b36",
  borderRadius: 12,
  background: "#0f1115"
};

const logsCardStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  padding: 16,
  border: "1px solid #262b36",
  borderRadius: 14,
  background: "#171a21"
};

function logItemStyle(level: "info" | "error"): CSSProperties {
  return {
    display: "grid",
    gap: 8,
    padding: 12,
    border: `1px solid ${level === "error" ? "#5a2a2a" : "#2c3b54"}`,
    borderRadius: 12,
    background: level === "error" ? "#221416" : "#131d2b",
  };
}

const footerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12
};
