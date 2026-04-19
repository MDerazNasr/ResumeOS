"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties } from "react";
import type { PatchHunkDto, PatchSetDto } from "@/lib/api/types";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
});

type LatexEditorProps = {
  activeHunkId: string | null;
  dismissedHunkIds: string[];
  editorMode?: "standard" | "vim";
  onApplyAll: () => Promise<void>;
  onApplyHunk: (patchSet: PatchSetDto, hunk: PatchHunkDto) => Promise<boolean>;
  value: string;
  onChange: (value: string) => void;
  onDismissAll: () => Promise<void>;
  onDismissHunk: (patchSet: PatchSetDto, hunk: PatchHunkDto) => Promise<boolean>;
  onNavigateHunk: (direction: "previous" | "next") => void;
  onSelectHunk: (hunkId: string | null) => void;
  patchSets: PatchSetDto[];
};

export function LatexEditor({
  activeHunkId,
  dismissedHunkIds,
  editorMode = "standard",
  onApplyAll,
  onApplyHunk,
  onChange,
  onDismissAll,
  onDismissHunk,
  onNavigateHunk,
  onSelectHunk,
  patchSets,
  value,
}: LatexEditorProps) {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const vimModeRef = useRef<{ dispose?: () => void } | null>(null);
  const statusRef = useRef<HTMLDivElement | null>(null);
  const decorationIdsRef = useRef<string[]>([]);
  const contentWidgetRef = useRef<any>(null);
  const mouseHandlerRef = useRef<{ dispose?: () => void } | null>(null);
  const keyHandlerRef = useRef<{ dispose?: () => void } | null>(null);
  const [vimStatus, setVimStatus] = useState("Standard editing");
  const [themeMode, setThemeMode] = useState<"dark" | "light">("light");
  const visiblePatchEntries = useMemo(
    () =>
      patchSets.flatMap((patchSet) =>
        patchSet.items
          .filter((hunk) => !dismissedHunkIds.includes(hunk.id))
          .map((hunk) => ({ patchSet, hunk })),
      ),
    [dismissedHunkIds, patchSets],
  );
  const activePatchEntry =
    visiblePatchEntries.find(({ hunk }) => hunk.id === activeHunkId) ?? visiblePatchEntries[0] ?? null;

  useEffect(() => {
    const editor = editorRef.current;
    const statusNode = statusRef.current;

    if (!editor || !statusNode) {
      return;
    }

    vimModeRef.current?.dispose?.();
    vimModeRef.current = null;

    if (editorMode === "vim") {
      let isDisposed = false;
      let observer: MutationObserver | null = null;

      void import("monaco-vim").then(({ initVimMode }) => {
        if (isDisposed) {
          return;
        }

        vimModeRef.current = initVimMode(editor, statusNode);
        setVimStatus(statusNode.textContent?.trim() || "Vim mode");
        observer = new MutationObserver(() => {
          setVimStatus(statusNode.textContent?.trim() || "Vim mode");
        });
        observer.observe(statusNode, { childList: true, subtree: true, characterData: true });
      });

      return () => {
        isDisposed = true;
        observer?.disconnect();
        vimModeRef.current?.dispose?.();
        vimModeRef.current = null;
      };
    }

    setVimStatus("Standard editing");
    statusNode.textContent = "";

    return () => {
      vimModeRef.current?.dispose?.();
      vimModeRef.current = null;
    };
  }, [editorMode]);

  useEffect(() => {
    const applyTheme = () => {
      const nextTheme = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
      setThemeMode(nextTheme);
    };

    applyTheme();

    const observer = new MutationObserver(() => {
      applyTheme();
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

    return () => {
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;

    if (!editor || !monaco) {
      return;
    }

    monaco.editor.setTheme(themeMode === "light" ? "vs" : "vs-dark");
  }, [themeMode]);

  useEffect(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;

    if (!editor || !monaco) {
      return;
    }

    decorationIdsRef.current = editor.deltaDecorations(
      decorationIdsRef.current,
      visiblePatchEntries.map(({ hunk }) => ({
        range: new monaco.Range(hunk.startLine, 1, hunk.endLine, 1),
        options: {
          isWholeLine: true,
          className:
            hunk.id === activePatchEntry?.hunk.id ? "resumeos-inline-hunk-active" : "resumeos-inline-hunk-remove",
          linesDecorationsClassName:
            hunk.id === activePatchEntry?.hunk.id ? "resumeos-inline-glyph-active" : "resumeos-inline-glyph",
          glyphMarginClassName:
            hunk.id === activePatchEntry?.hunk.id ? "resumeos-inline-glyph-active" : "resumeos-inline-glyph",
          hoverMessage: {
            value: `Patch hunk: ${hunk.label}`,
          },
        },
      })),
    );

    if (activePatchEntry) {
      editor.revealLineInCenter(activePatchEntry.hunk.startLine);
    }
  }, [activePatchEntry, visiblePatchEntries]);

  useEffect(() => {
    const editor = editorRef.current;

    if (!editor) {
      return;
    }

    mouseHandlerRef.current?.dispose?.();
    mouseHandlerRef.current = editor.onMouseDown((event: any) => {
      const lineNumber = event.target.position?.lineNumber;
      if (!lineNumber) {
        return;
      }

      const matchingHunk = visiblePatchEntries.find(
        ({ hunk }) => lineNumber >= hunk.startLine && lineNumber <= hunk.endLine,
      );

      if (matchingHunk) {
        onSelectHunk(matchingHunk.hunk.id);
      }
    });

    return () => {
      mouseHandlerRef.current?.dispose?.();
      mouseHandlerRef.current = null;
    };
  }, [onSelectHunk, visiblePatchEntries]);

  useEffect(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;

    if (!editor || !monaco) {
      return;
    }

    keyHandlerRef.current?.dispose?.();
    keyHandlerRef.current = editor.onKeyDown((event: any) => {
      if (!activePatchEntry) {
        return;
      }

      const isPrimary = event.ctrlKey || event.metaKey;

      if (isPrimary && event.shiftKey && event.keyCode === monaco.KeyCode.Enter) {
        event.preventDefault();
        event.stopPropagation();
        void onApplyAll();
        return;
      }

      if (event.shiftKey && event.keyCode === monaco.KeyCode.Escape) {
        event.preventDefault();
        event.stopPropagation();
        void onDismissAll();
        return;
      }

      if (isPrimary && event.keyCode === monaco.KeyCode.Enter) {
        event.preventDefault();
        event.stopPropagation();
        void onApplyHunk(activePatchEntry.patchSet, activePatchEntry.hunk);
        return;
      }

      if (event.keyCode === monaco.KeyCode.Escape) {
        event.preventDefault();
        event.stopPropagation();
        void onDismissHunk(activePatchEntry.patchSet, activePatchEntry.hunk);
        return;
      }

      if (event.altKey && event.keyCode === monaco.KeyCode.BracketRight) {
        event.preventDefault();
        event.stopPropagation();
        onNavigateHunk("next");
        return;
      }

      if (event.altKey && event.keyCode === monaco.KeyCode.BracketLeft) {
        event.preventDefault();
        event.stopPropagation();
        onNavigateHunk("previous");
      }
    });

    return () => {
      keyHandlerRef.current?.dispose?.();
      keyHandlerRef.current = null;
    };
  }, [activePatchEntry, onApplyAll, onApplyHunk, onDismissAll, onDismissHunk, onNavigateHunk]);

  useEffect(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;

    if (!editor || !monaco) {
      return;
    }

    if (contentWidgetRef.current) {
      editor.removeContentWidget(contentWidgetRef.current);
      contentWidgetRef.current = null;
    }

    if (!activePatchEntry) {
      return;
    }

    const widgetNode = document.createElement("div");
    widgetNode.className = "resumeos-inline-widget";

    const titleNode = document.createElement("div");
    titleNode.className = "resumeos-inline-widget-title";

    const titleTextNode = document.createElement("span");
    titleTextNode.className = "resumeos-inline-widget-title-text";
    titleTextNode.textContent = activePatchEntry.hunk.label;

    const titleMetaNode = document.createElement("span");
    titleMetaNode.className = "resumeos-inline-widget-title-meta";
    titleMetaNode.textContent = `${activePatchEntry.patchSet.mode} • lines ${activePatchEntry.hunk.startLine}-${activePatchEntry.hunk.endLine}`;

    titleNode.appendChild(titleTextNode);
    titleNode.appendChild(titleMetaNode);

    const shortcutsNode = document.createElement("div");
    shortcutsNode.className = "resumeos-inline-widget-shortcuts";
    shortcutsNode.textContent =
      "Cmd/Ctrl+Enter accept • Esc reject • Alt+[ / Alt+] navigate • Cmd/Ctrl+Shift+Enter accept all • Shift+Esc reject all";

    const diffGridNode = document.createElement("div");
    diffGridNode.className = "resumeos-inline-widget-diff-grid";

    const beforeNode = document.createElement("pre");
    beforeNode.className = "resumeos-inline-widget-before";
    beforeNode.textContent = `- ${activePatchEntry.hunk.beforeText}`;

    const afterNode = document.createElement("pre");
    afterNode.className = "resumeos-inline-widget-after";
    afterNode.textContent = `+ ${activePatchEntry.hunk.afterText}`;

    diffGridNode.appendChild(beforeNode);
    diffGridNode.appendChild(afterNode);

    const actionRow = document.createElement("div");
    actionRow.className = "resumeos-inline-widget-actions";

    const applyButton = document.createElement("button");
    applyButton.className = "resumeos-inline-widget-apply";
    applyButton.textContent = "Accept";
    applyButton.onclick = (event) => {
      event.preventDefault();
      event.stopPropagation();
      void onApplyHunk(activePatchEntry.patchSet, activePatchEntry.hunk);
    };

    const rejectButton = document.createElement("button");
    rejectButton.className = "resumeos-inline-widget-reject";
    rejectButton.textContent = "Reject";
    rejectButton.onclick = (event) => {
      event.preventDefault();
      event.stopPropagation();
      void onDismissHunk(activePatchEntry.patchSet, activePatchEntry.hunk);
    };

    const previousButton = document.createElement("button");
    previousButton.className = "resumeos-inline-widget-secondary";
    previousButton.textContent = "Previous";
    previousButton.onclick = (event) => {
      event.preventDefault();
      event.stopPropagation();
      onNavigateHunk("previous");
    };

    const nextButton = document.createElement("button");
    nextButton.className = "resumeos-inline-widget-secondary";
    nextButton.textContent = "Next";
    nextButton.onclick = (event) => {
      event.preventDefault();
      event.stopPropagation();
      onNavigateHunk("next");
    };

    const acceptAllButton = document.createElement("button");
    acceptAllButton.className = "resumeos-inline-widget-secondary";
    acceptAllButton.textContent = "Approve All";
    acceptAllButton.onclick = (event) => {
      event.preventDefault();
      event.stopPropagation();
      void onApplyAll();
    };

    const rejectAllButton = document.createElement("button");
    rejectAllButton.className = "resumeos-inline-widget-secondary";
    rejectAllButton.textContent = "Reject All";
    rejectAllButton.onclick = (event) => {
      event.preventDefault();
      event.stopPropagation();
      void onDismissAll();
    };

    actionRow.appendChild(previousButton);
    actionRow.appendChild(nextButton);
    actionRow.appendChild(applyButton);
    actionRow.appendChild(rejectButton);
    actionRow.appendChild(acceptAllButton);
    actionRow.appendChild(rejectAllButton);

    widgetNode.appendChild(titleNode);
    widgetNode.appendChild(diffGridNode);
    widgetNode.appendChild(actionRow);
    widgetNode.appendChild(shortcutsNode);

    const widget = {
      allowEditorOverflow: true,
      domNode: widgetNode,
      getDomNode() {
        return widgetNode;
      },
      getId() {
        return `resumeos-inline-widget-${activePatchEntry.hunk.id}`;
      },
      getPosition() {
        return {
          position: { lineNumber: activePatchEntry.hunk.endLine, column: 1 },
          preference: [monaco.editor.ContentWidgetPositionPreference.BELOW],
        };
      },
    };

    contentWidgetRef.current = widget;
    editor.addContentWidget(widget);

    return () => {
      if (contentWidgetRef.current) {
        editor.removeContentWidget(contentWidgetRef.current);
        contentWidgetRef.current = null;
      }
    };
  }, [activePatchEntry, onApplyAll, onApplyHunk, onDismissAll, onDismissHunk]);

  return (
    <div style={editorShellStyle}>
      <MonacoEditor
        defaultLanguage="latex"
        height="70vh"
        onChange={(nextValue) => onChange(nextValue ?? "")}
        onMount={(editor, monaco) => {
          editorRef.current = editor;
          monacoRef.current = monaco;
        }}
        options={{
          automaticLayout: true,
          fontSize: 14,
          glyphMargin: true,
          lineNumbers: "on",
          minimap: { enabled: false },
          padding: { top: 16, bottom: 16 },
          scrollBeyondLastLine: false,
          wordWrap: "on",
        }}
        theme={themeMode === "light" ? "vs" : "vs-dark"}
        value={value}
      />
      <div style={statusBarStyle}>
        <span style={statusTextStyle}>{editorMode === "vim" ? vimStatus || "Vim mode" : "Standard editing"}</span>
        <div ref={statusRef} style={hiddenVimStatusStyle} />
      </div>
    </div>
  );
}

const editorShellStyle: CSSProperties = {
  display: "grid",
  overflow: "hidden",
  border: "1px solid var(--border-strong)",
  borderRadius: 16,
  background: "var(--surface)",
};

const statusBarStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 12,
  padding: "10px 14px",
  borderTop: "1px solid var(--border-strong)",
  background: "var(--surface-muted)",
};

const statusTextStyle: CSSProperties = {
  color: "var(--muted)",
  fontSize: 12,
  fontFamily: "var(--font-geist-mono, monospace)",
  letterSpacing: "0.02em",
};

const hiddenVimStatusStyle: CSSProperties = {
  position: "absolute",
  width: 0,
  height: 0,
  overflow: "hidden",
  opacity: 0,
  pointerEvents: "none",
};

if (typeof document !== "undefined" && !document.getElementById("resumeos-inline-review-styles")) {
  const styleTag = document.createElement("style");
  styleTag.id = "resumeos-inline-review-styles";
  styleTag.textContent = `
    .resumeos-inline-hunk-remove {
      background: rgba(247, 96, 96, 0.10);
      border-left: 2px solid rgba(247, 96, 96, 0.75);
    }
    .resumeos-inline-hunk-active {
      background: linear-gradient(90deg, rgba(247, 96, 96, 0.12), rgba(92, 154, 255, 0.08));
      border-left: 2px solid rgba(92, 154, 255, 0.92);
      outline: 1px solid rgba(92, 154, 255, 0.22);
    }
    .resumeos-inline-glyph,
    .resumeos-inline-glyph-active {
      width: 10px !important;
      margin-left: 4px;
      border-radius: 999px;
    }
    .resumeos-inline-glyph {
      background: rgba(190, 78, 78, 0.85);
    }
    .resumeos-inline-glyph-active {
      background: rgba(75, 137, 255, 0.95);
    }
    .resumeos-inline-widget {
      width: min(560px, calc(100vw - 120px));
      display: grid;
      gap: 12px;
      margin-top: 8px;
      padding: 14px;
      border: 1px solid rgba(81, 92, 117, 0.72);
      border-radius: 14px;
      background: rgba(19, 23, 31, 0.98);
      box-shadow: 0 18px 42px rgba(0, 0, 0, 0.34);
      color: #e7ecf3;
      font-family: var(--font-geist-mono, monospace);
      font-size: 12px;
      line-height: 1.5;
      backdrop-filter: blur(10px);
    }
    .resumeos-inline-widget-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .resumeos-inline-widget-title-text {
      font-weight: 700;
      font-size: 12px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #dbe8ff;
    }
    .resumeos-inline-widget-title-meta {
      padding: 4px 8px;
      border-radius: 999px;
      background: rgba(74, 85, 109, 0.42);
      color: #92a2bb;
      font-size: 10px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .resumeos-inline-widget-shortcuts {
      color: #7f8ca3;
      font-size: 10px;
      line-height: 1.5;
    }
    .resumeos-inline-widget-diff-grid {
      display: grid;
      gap: 8px;
    }
    .resumeos-inline-widget-before,
    .resumeos-inline-widget-after {
      margin: 0;
      padding: 10px 12px;
      border-radius: 10px;
      white-space: pre-wrap;
      border: 1px solid transparent;
    }
    .resumeos-inline-widget-before {
      background: rgba(247, 96, 96, 0.10);
      color: #ffb2b2;
      border-color: rgba(247, 96, 96, 0.22);
    }
    .resumeos-inline-widget-after {
      background: rgba(76, 201, 126, 0.10);
      color: #a8efbe;
      border-color: rgba(76, 201, 126, 0.22);
    }
    .resumeos-inline-widget-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .resumeos-inline-widget-actions button {
      padding: 6px 10px;
      border-radius: 8px;
      border: 1px solid rgba(90, 102, 128, 0.45);
      cursor: pointer;
      font: inherit;
      transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
    }
    .resumeos-inline-widget-actions button:hover {
      transform: translateY(-1px);
    }
    .resumeos-inline-widget-apply {
      background: rgba(76, 201, 126, 0.14);
      color: #a8efbe;
      border-color: rgba(76, 201, 126, 0.28);
    }
    .resumeos-inline-widget-reject {
      background: rgba(247, 96, 96, 0.14);
      color: #ffb2b2;
      border-color: rgba(247, 96, 96, 0.28);
    }
    .resumeos-inline-widget-secondary {
      background: rgba(62, 72, 92, 0.55);
      color: #d3dcea;
      border-color: rgba(96, 110, 139, 0.34);
    }
  `;
  document.head.appendChild(styleTag);
}
