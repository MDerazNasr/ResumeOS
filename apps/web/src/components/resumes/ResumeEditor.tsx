"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties } from "react";
import { applyPatch, compileDraft, generateEditSuggestions, generateReviewSuggestions, generateTailorSuggestions, getDocumentModel, getSeededPatchSets, getUserSettings, logFeedback, saveDraft, updateUserSettings } from "@/lib/api/client";
import { ChatSidebar } from "@/components/resumes/ChatSidebar";
import { DocumentModelPanel } from "@/components/resumes/DocumentModelPanel";
import { LatexEditor } from "@/components/resumes/LatexEditor";
import { PatchSetReviewPanel } from "@/components/resumes/PatchSetReviewPanel";
import { SnapshotPanel } from "@/components/resumes/SnapshotPanel";
import type {
  ChatMessageDto,
  CompileResultDto,
  DocumentModelDto,
  EditableBlockDto,
  PatchHunkDto,
  PatchSetDto,
  ResumeDto,
  SnapshotDto,
  WorkingDraftDto,
} from "@/lib/api/types";

type ResumeEditorProps = {
  documentModel: DocumentModelDto;
  draft: WorkingDraftDto;
  initialChatMessages: ChatMessageDto[];
  initialSnapshots: SnapshotDto[];
  resume: ResumeDto;
};

type PatchSetRequestContext =
  | { mode: "mock"; seed: number }
  | { mode: "edit"; targetBlockId: string; instruction: string }
  | { mode: "review"; instruction: string }
  | { mode: "tailor"; instruction: string; jobDescription: string };

const EDITOR_MODE_STORAGE_KEY = "resumeos.editorMode";

export function ResumeEditor({ documentModel, draft, initialChatMessages, initialSnapshots, resume }: ResumeEditorProps) {
  const patchReviewRef = useRef<HTMLDivElement | null>(null);
  const [documentModelState, setDocumentModelState] = useState(documentModel);
  const [editorMode, setEditorMode] = useState<"standard" | "vim">("standard");
  const [patchSets, setPatchSets] = useState<PatchSetDto[]>([]);
  const [dismissedPatchHunkIds, setDismissedPatchHunkIds] = useState<string[]>([]);
  const [activePatchHunkId, setActivePatchHunkId] = useState<string | null>(null);
  const [seededPatchSetSeed, setSeededPatchSetSeed] = useState(0);
  const [persistedSourceTex, setPersistedSourceTex] = useState(draft.sourceTex);
  const [sourceTex, setSourceTex] = useState(draft.sourceTex);
  const [version, setVersion] = useState(draft.version);
  const [updatedAt, setUpdatedAt] = useState(draft.updatedAt);
  const [isSaving, setIsSaving] = useState(false);
  const [isCompiling, setIsCompiling] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [isTailoring, setIsTailoring] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activityMessage, setActivityMessage] = useState<string | null>(null);
  const [patchSetEmptyMessage, setPatchSetEmptyMessage] = useState<string | null>(null);
  const [compileResult, setCompileResult] = useState<CompileResultDto | null>(null);
  const [previewNonce, setPreviewNonce] = useState<number>(0);
  const [jobDescription, setJobDescription] = useState("");
  const [snapshotRefreshToken, setSnapshotRefreshToken] = useState(0);
  const [lastPatchSetRequest, setLastPatchSetRequest] = useState<PatchSetRequestContext>({ mode: "mock", seed: 0 });
  const saveInFlightRef = useRef<Promise<WorkingDraftDto | null> | null>(null);
  const editorModeHydratedRef = useRef(false);
  const sourceTexRef = useRef(sourceTex);
  const persistedSourceTexRef = useRef(persistedSourceTex);
  const versionRef = useRef(version);

  const isDirty = useMemo(() => sourceTex !== persistedSourceTex, [persistedSourceTex, sourceTex]);
  const visiblePatchEntries = useMemo(
    () =>
      patchSets.flatMap((patchSet) =>
        patchSet.items
          .filter((hunk) => !dismissedPatchHunkIds.includes(hunk.id))
          .map((hunk) => ({ patchSet, hunk })),
      ),
    [dismissedPatchHunkIds, patchSets],
  );

  useEffect(() => {
    sourceTexRef.current = sourceTex;
  }, [sourceTex]);

  useEffect(() => {
    persistedSourceTexRef.current = persistedSourceTex;
  }, [persistedSourceTex]);

  useEffect(() => {
    versionRef.current = version;
  }, [version]);

  useEffect(() => {
    const visibleHunks = patchSets.flatMap((patchSet) =>
      patchSet.items.filter((hunk) => !dismissedPatchHunkIds.includes(hunk.id)),
    );

    if (visibleHunks.length === 0) {
      if (activePatchHunkId !== null) {
        setActivePatchHunkId(null);
      }
      return;
    }

    if (!activePatchHunkId || !visibleHunks.some((hunk) => hunk.id === activePatchHunkId)) {
      setActivePatchHunkId(visibleHunks[0]?.id ?? null);
    }
  }, [activePatchHunkId, dismissedPatchHunkIds, patchSets]);

  function focusPatchReview() {
    patchReviewRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function buildPatchSetSummary(items: PatchSetDto[], emptyLabel: string) {
    if (items.length === 0) {
      return emptyLabel;
    }

    const hunkCount = items.reduce((total, patchSet) => total + patchSet.items.length, 0);
    return `Loaded ${items.length} patch set${items.length === 1 ? "" : "s"} with ${hunkCount} hunk${hunkCount === 1 ? "" : "s"}.`;
  }

  function loadPatchSets(items: PatchSetDto[], emptyLabel: string | null = null, activityLabel: string | null = null) {
    setPatchSets(items);
    setDismissedPatchHunkIds([]);
    setPatchSetEmptyMessage(emptyLabel);
    if (activityLabel) {
      setActivityMessage(activityLabel);
    }
    focusPatchReview();
  }

  useEffect(() => {
    try {
      const storedMode = window.localStorage.getItem(EDITOR_MODE_STORAGE_KEY);
      if (storedMode === "standard" || storedMode === "vim") {
        setEditorMode(storedMode);
      }
    } catch {
      return;
    }

    void getUserSettings()
      .then((settings) => {
        setEditorMode(settings.editorMode);
        try {
          window.localStorage.setItem(EDITOR_MODE_STORAGE_KEY, settings.editorMode);
        } catch {
          return;
        }
      })
      .catch(() => null)
      .finally(() => {
        editorModeHydratedRef.current = true;
      });
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(EDITOR_MODE_STORAGE_KEY, editorMode);
    } catch {
      // keep going so backend settings can still persist
    }

    if (!editorModeHydratedRef.current) {
      return;
    }

    void updateUserSettings({ editorMode }).catch(() => null);
  }, [editorMode]);

  async function saveLatestDraft() {
    if (sourceTexRef.current === persistedSourceTexRef.current) {
      return null;
    }

    setIsSaving(true);
    setError(null);
    setActivityMessage(null);

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
      const [nextDocumentModel, nextPatchSets] = await Promise.all([
        getDocumentModel(resume.id),
        getSeededPatchSets(resume.id, seededPatchSetSeed),
      ]);
      setDocumentModelState(nextDocumentModel);
      setPatchSets(nextPatchSets.items);
      setDismissedPatchHunkIds([]);
      setPatchSetEmptyMessage(null);
      setLastPatchSetRequest({ mode: "mock", seed: seededPatchSetSeed });
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
    setActivityMessage(null);

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
      setActivityMessage(result.status === "success" ? "Compile succeeded. Preview updated." : "Compile returned errors.");
    } catch (compileError) {
      setError(compileError instanceof Error ? compileError.message : "Failed to compile draft.");
    } finally {
      setIsCompiling(false);
    }
  }

  async function handleApplyPatchSetHunk(patchSet: PatchSetDto, hunk: PatchHunkDto) {
    setError(null);
    setActivityMessage(null);

    try {
      const updatedDraft = await applyPatch(resume.id, {
        targetBlockId: hunk.targetBlockId,
        startLine: hunk.startLine,
        endLine: hunk.endLine,
        beforeText: hunk.beforeText,
        afterText: hunk.afterText,
      });
      await logFeedback(resume.id, {
        suggestionMode: patchSet.mode,
        action: "apply",
        suggestionSetId: patchSet.id,
        proposalId: hunk.id,
        targetBlockId: hunk.targetBlockId,
      });

      sourceTexRef.current = updatedDraft.sourceTex;
      persistedSourceTexRef.current = updatedDraft.sourceTex;
      versionRef.current = updatedDraft.version;
      setPersistedSourceTex(updatedDraft.sourceTex);
      setSourceTex(updatedDraft.sourceTex);
      setVersion(updatedDraft.version);
      setUpdatedAt(updatedDraft.updatedAt);
      setCompileResult(null);
      setDismissedPatchHunkIds((current) => (current.includes(hunk.id) ? current : [...current, hunk.id]));

      const nextDocumentModel = await getDocumentModel(resume.id);
      setDocumentModelState(nextDocumentModel);
      setPatchSetEmptyMessage(null);
      setActivityMessage(`Applied "${hunk.label}" to the working draft.`);
      return true;
    } catch (applyError) {
      setError(applyError instanceof Error ? applyError.message : "Failed to apply patch.");
      return false;
    }
  }

  async function handleDismissPatchSetHunk(patchSet: PatchSetDto, hunk: PatchHunkDto) {
    try {
      setError(null);
      setActivityMessage(null);
      await logFeedback(resume.id, {
        suggestionMode: patchSet.mode,
        action: "dismiss",
        suggestionSetId: patchSet.id,
        proposalId: hunk.id,
        targetBlockId: hunk.targetBlockId,
      });
      setDismissedPatchHunkIds((current) => [...current, hunk.id]);
      setActivityMessage(`Rejected "${hunk.label}".`);
      return true;
    } catch (dismissError) {
      setError(dismissError instanceof Error ? dismissError.message : "Failed to record suggestion feedback.");
      return false;
    }
  }

  function handleSnapshotRestore(restoredDraft: WorkingDraftDto) {
    setPersistedSourceTex(restoredDraft.sourceTex);
    setSourceTex(restoredDraft.sourceTex);
    setVersion(restoredDraft.version);
    setUpdatedAt(restoredDraft.updatedAt);
    setCompileResult(null);
    setError(null);
    setActivityMessage("Snapshot restored into the working draft.");
    void Promise.all([getDocumentModel(resume.id), getSeededPatchSets(resume.id, seededPatchSetSeed)])
      .then(([nextDocumentModel, nextPatchSets]) => {
        setDocumentModelState(nextDocumentModel);
        setPatchSets(nextPatchSets.items);
        setDismissedPatchHunkIds([]);
        setPatchSetEmptyMessage(null);
        setLastPatchSetRequest({ mode: "mock", seed: seededPatchSetSeed });
      })
      .catch(() => null);
  }

  useEffect(() => {
    void getSeededPatchSets(resume.id, seededPatchSetSeed)
      .then((result) => {
        setPatchSets(result.items);
        setDismissedPatchHunkIds([]);
        setPatchSetEmptyMessage(null);
        setLastPatchSetRequest({ mode: "mock", seed: seededPatchSetSeed });
      })
      .catch(() => null);
  }, [resume.id, seededPatchSetSeed]);

  async function handleRetryPatchSet(patchSet: PatchSetDto) {
    setError(null);
    setActivityMessage(null);
    setPatchSetEmptyMessage(null);

    if (patchSet.mode === "mock") {
      const nextSeed = patchSet.retrySeed;
      setSeededPatchSetSeed(nextSeed);
      setActivityMessage("Loaded a new seeded patch set.");
      focusPatchReview();
      return;
    }

    try {
      if (lastPatchSetRequest.mode === "edit") {
        const generated = await generateEditSuggestions(resume.id, {
          targetBlockId: lastPatchSetRequest.targetBlockId,
          instruction: lastPatchSetRequest.instruction,
        });
        loadPatchSets(
          generated.items,
          generated.items.length === 0 ? "No valid edit suggestions were generated for that block." : null,
          buildPatchSetSummary(generated.items, "No valid edit suggestions were generated."),
        );
        return;
      }

      if (lastPatchSetRequest.mode === "review") {
        const generated = await generateReviewSuggestions(resume.id, {
          instruction: lastPatchSetRequest.instruction,
        });
        loadPatchSets(
          generated.items,
          generated.items.length === 0 ? "No valid review suggestions were generated for the current draft." : null,
          buildPatchSetSummary(generated.items, "No valid review suggestions were generated."),
        );
        return;
      }

      if (lastPatchSetRequest.mode === "tailor") {
        const generated = await generateTailorSuggestions(resume.id, {
          jobDescription: lastPatchSetRequest.jobDescription,
          instruction: lastPatchSetRequest.instruction,
        });
        loadPatchSets(
          generated.items,
          generated.items.length === 0 ? "No valid tailoring suggestions were generated for that job description." : null,
          buildPatchSetSummary(generated.items, "No valid tailoring suggestions were generated."),
        );
        setSnapshotRefreshToken((current) => current + 1);
      }
    } catch (retryError) {
      setError(retryError instanceof Error ? retryError.message : "Failed to regenerate suggestions.");
    }
  }

  function moveActivePatchHunk(direction: "previous" | "next") {
    if (visiblePatchEntries.length === 0) {
      return;
    }

    const currentIndex = visiblePatchEntries.findIndex(({ hunk }) => hunk.id === activePatchHunkId);
    const nextIndex =
      direction === "previous"
        ? Math.max(0, (currentIndex === -1 ? 0 : currentIndex) - 1)
        : Math.min(visiblePatchEntries.length - 1, (currentIndex === -1 ? 0 : currentIndex) + 1);

    setActivePatchHunkId(visiblePatchEntries[nextIndex]?.hunk.id ?? null);
  }

  async function handleApplyAllVisiblePatchHunks() {
    setError(null);
    setActivityMessage(null);

    const currentEntries = [...visiblePatchEntries];
    if (currentEntries.length === 0) {
      return;
    }

    let appliedCount = 0;

    for (const entry of currentEntries) {
      const applied = await handleApplyPatchSetHunk(entry.patchSet, entry.hunk);
      if (!applied) {
        break;
      }
      appliedCount += 1;
    }

    setActivePatchHunkId(null);
    if (appliedCount > 0) {
      setActivityMessage(`Approved ${appliedCount} hunk${appliedCount === 1 ? "" : "s"}.`);
    }
  }

  async function handleRejectAllVisiblePatchHunks() {
    setError(null);
    setActivityMessage(null);

    const currentEntries = [...visiblePatchEntries];
    if (currentEntries.length === 0) {
      return;
    }

    let rejectedCount = 0;

    for (const entry of currentEntries) {
      const dismissed = await handleDismissPatchSetHunk(entry.patchSet, entry.hunk);
      if (!dismissed) {
        break;
      }
      rejectedCount += 1;
    }

    setActivePatchHunkId(null);
    if (rejectedCount > 0) {
      setActivityMessage(`Rejected ${rejectedCount} hunk${rejectedCount === 1 ? "" : "s"}.`);
    }
  }

  async function handleSuggestEdit(block: EditableBlockDto, instruction: string) {
    setError(null);
    setActivityMessage(null);
    setPatchSetEmptyMessage(null);

    try {
      const generated = await generateEditSuggestions(resume.id, {
        targetBlockId: block.id,
        instruction,
      });
      loadPatchSets(
        generated.items,
        generated.items.length === 0 ? "No valid edit suggestions were generated for that block." : null,
        buildPatchSetSummary(generated.items, "No valid edit suggestions were generated."),
      );
      setLastPatchSetRequest({ mode: "edit", targetBlockId: block.id, instruction });
    } catch (suggestError) {
      setError(suggestError instanceof Error ? suggestError.message : "Failed to generate edit suggestions.");
    }
  }

  async function handleReviewResume() {
    setError(null);
    setIsReviewing(true);
    setActivityMessage(null);
    setPatchSetEmptyMessage(null);

    try {
      const instruction = "Review the current resume and suggest stronger wording for the weakest editable blocks.";
      const generated = await generateReviewSuggestions(resume.id, { instruction });
      loadPatchSets(
        generated.items,
        generated.items.length === 0 ? "No valid review suggestions were generated for the current draft." : null,
        buildPatchSetSummary(generated.items, "No valid review suggestions were generated."),
      );
      setLastPatchSetRequest({ mode: "review", instruction });
    } catch (reviewError) {
      setError(reviewError instanceof Error ? reviewError.message : "Failed to generate review suggestions.");
    } finally {
      setIsReviewing(false);
    }
  }

  async function handleTailorResume() {
    const trimmedDescription = jobDescription.trim();

    if (trimmedDescription.length < 20) {
      setError("Job description must be at least 20 characters to generate tailoring suggestions.");
      setActivityMessage(null);
      return;
    }

    setError(null);
    setIsTailoring(true);
    setActivityMessage(null);
    setPatchSetEmptyMessage(null);

    try {
      const draftReady = await ensureLatestDraftSaved();
      if (!draftReady) {
        return;
      }

      const instruction = "Tailor the resume wording toward the most important requirements in this job description.";
      const generated = await generateTailorSuggestions(resume.id, {
        jobDescription: trimmedDescription,
        instruction,
      });
      loadPatchSets(
        generated.items,
        generated.items.length === 0 ? "No valid tailoring suggestions were generated for that job description." : null,
        buildPatchSetSummary(generated.items, "No valid tailoring suggestions were generated."),
      );
      setLastPatchSetRequest({ mode: "tailor", instruction, jobDescription: trimmedDescription });
      setSnapshotRefreshToken((current) => current + 1);
    } catch (tailorError) {
      setError(tailorError instanceof Error ? tailorError.message : "Failed to generate tailoring suggestions.");
    } finally {
      setIsTailoring(false);
    }
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
            <button
              disabled={isSaving || isCompiling || isReviewing || isTailoring}
              onClick={handleReviewResume}
              style={secondaryButtonStyle}
              type="button"
            >
              {isReviewing ? "Reviewing..." : "Review Resume"}
            </button>
            <button
              disabled={isSaving || isCompiling || isReviewing || isTailoring}
              onClick={handleCompile}
              style={secondaryButtonStyle}
              type="button"
            >
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
          <div style={editorModeToggleStyle}>
            <span style={{ color: "#9ba3b4", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Editor
            </span>
            <div style={editorModeButtonGroupStyle}>
              <button
                onClick={() => setEditorMode("standard")}
                style={editorModeButtonStyle(editorMode === "standard")}
                type="button"
              >
                Standard
              </button>
              <button
                onClick={() => setEditorMode("vim")}
                style={editorModeButtonStyle(editorMode === "vim")}
                type="button"
              >
                Vim
              </button>
            </div>
          </div>
        </div>
      </div>
      {error ? <div style={errorBannerStyle}>{error}</div> : null}
      {!error && activityMessage ? <div style={activityBannerStyle}>{activityMessage}</div> : null}
      <div style={workspaceStyle}>
        <LatexEditor
          activeHunkId={activePatchHunkId}
          dismissedHunkIds={dismissedPatchHunkIds}
          editorMode={editorMode}
          onApplyAll={handleApplyAllVisiblePatchHunks}
          onApplyHunk={handleApplyPatchSetHunk}
          onChange={setSourceTex}
          onDismissAll={handleRejectAllVisiblePatchHunks}
          onDismissHunk={handleDismissPatchSetHunk}
          onNavigateHunk={moveActivePatchHunk}
          onSelectHunk={setActivePatchHunkId}
          patchSets={patchSets}
          value={sourceTex}
        />
        <aside style={panelStyle}>
          <ChatSidebar
            initialMessages={initialChatMessages}
            onPatchSetsGenerated={(items) =>
              loadPatchSets(
                items,
                items.length === 0 ? "Chat did not produce any valid patch sets." : null,
                buildPatchSetSummary(items, "Chat did not produce any valid patch sets."),
              )
            }
            resumeId={resume.id}
          />
          <div ref={patchReviewRef}>
            <PatchSetReviewPanel
              activeHunkId={activePatchHunkId}
              dismissedIds={dismissedPatchHunkIds}
              emptyMessage={patchSetEmptyMessage}
              isLoading={isReviewing || isTailoring}
              onActiveHunkChange={setActivePatchHunkId}
              onApply={handleApplyPatchSetHunk}
              onDismiss={handleDismissPatchSetHunk}
              onRetrySet={handleRetryPatchSet}
              patchSets={patchSets}
            />
          </div>
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
          <div style={tailorCardStyle}>
            <strong style={{ fontSize: 15 }}>Tailor Resume</strong>
            <p style={{ margin: 0, color: "#9ba3b4", lineHeight: 1.6 }}>
              Paste a job description to generate a small set of validated tailoring suggestions.
            </p>
            <textarea
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste a job description here..."
              style={tailorTextareaStyle}
              value={jobDescription}
            />
            <button
              disabled={isSaving || isCompiling || isReviewing || isTailoring}
              onClick={handleTailorResume}
              style={secondaryButtonStyle}
              type="button"
            >
              {isTailoring ? "Tailoring..." : "Tailor Resume"}
            </button>
          </div>
          <DocumentModelPanel documentModel={documentModelState} onSuggestEdit={handleSuggestEdit} />
          <SnapshotPanel
            currentSourceTex={sourceTex}
            ensureLatestDraft={ensureLatestDraftSaved}
            initialSnapshots={initialSnapshots}
            onRestore={handleSnapshotRestore}
            refreshToken={snapshotRefreshToken}
            resumeId={resume.id}
          />
        </aside>
      </div>
      <div style={footerStyle}>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>Draft version {version}</span>
        {activityMessage && !error ? <span style={{ color: "var(--muted)", fontSize: 13 }}>{activityMessage}</span> : null}
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

const editorModeToggleStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  justifyItems: "end",
};

const editorModeButtonGroupStyle: CSSProperties = {
  display: "inline-flex",
  gap: 8,
};

function editorModeButtonStyle(isActive: boolean): CSSProperties {
  return {
    padding: "8px 10px",
    border: `1px solid ${isActive ? "var(--mode-review-fg)" : "var(--border-strong)"}`,
    borderRadius: 10,
    background: isActive ? "var(--mode-review-bg)" : "var(--surface)",
    color: isActive ? "var(--mode-review-fg)" : "var(--fg)",
    cursor: "pointer",
    fontSize: 12,
    fontWeight: 600,
  };
}

const secondaryButtonStyle: CSSProperties = {
  padding: "10px 14px",
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--surface)",
  color: "var(--fg)",
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
  border: "1px solid var(--border)",
  borderRadius: 16,
  background: "var(--surface-alt)"
};

const statusCardStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  padding: 16,
  border: "1px solid var(--border)",
  borderRadius: 14,
  background: "var(--surface)"
};

const previewCardStyle: CSSProperties = {
  display: "grid",
  gap: 10,
  padding: 16,
  border: "1px solid var(--border)",
  borderRadius: 14,
  background: "var(--surface)"
};

const previewFrameStyle: CSSProperties = {
  width: "100%",
  minHeight: 440,
  border: "1px solid var(--border)",
  borderRadius: 12,
  background: "var(--surface-input)"
};

const logsCardStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  padding: 16,
  border: "1px solid var(--border)",
  borderRadius: 14,
  background: "var(--surface)"
};

const tailorCardStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  padding: 16,
  border: "1px solid var(--border)",
  borderRadius: 14,
  background: "var(--surface)"
};

const tailorTextareaStyle: CSSProperties = {
  minHeight: 140,
  width: "100%",
  resize: "vertical",
  padding: 12,
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--surface-input)",
  color: "var(--fg)",
  font: "inherit",
  lineHeight: 1.5
};

function logItemStyle(level: "info" | "error"): CSSProperties {
  return {
    display: "grid",
    gap: 8,
    padding: 12,
    border: `1px solid ${level === "error" ? "#b78585" : "var(--border-strong)"}`,
    borderRadius: 12,
    background: level === "error" ? "var(--diff-remove-bg)" : "var(--surface-elevated)",
  };
}

const footerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12
};

const errorBannerStyle: CSSProperties = {
  padding: "12px 14px",
  border: "1px solid #d58c8c",
  borderRadius: 12,
  background: "var(--diff-remove-bg)",
  color: "var(--diff-remove-fg)",
  fontSize: 14,
  lineHeight: 1.5,
};

const activityBannerStyle: CSSProperties = {
  padding: "12px 14px",
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--surface)",
  color: "var(--fg)",
  fontSize: 14,
  lineHeight: 1.5,
};
