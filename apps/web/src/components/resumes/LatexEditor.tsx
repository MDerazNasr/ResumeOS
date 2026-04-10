"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
});

type LatexEditorProps = {
  editorMode?: "standard" | "vim";
  value: string;
  onChange: (value: string) => void;
};

export function LatexEditor({ editorMode = "standard", value, onChange }: LatexEditorProps) {
  const editorRef = useRef<any>(null);
  const vimModeRef = useRef<{ dispose?: () => void } | null>(null);
  const statusRef = useRef<HTMLDivElement | null>(null);
  const [vimStatus, setVimStatus] = useState("Standard editing");

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

  return (
    <div style={editorShellStyle}>
      <MonacoEditor
        defaultLanguage="latex"
        height="70vh"
        onChange={(nextValue) => onChange(nextValue ?? "")}
        onMount={(editor) => {
          editorRef.current = editor;
        }}
        options={{
          automaticLayout: true,
          fontSize: 14,
          lineNumbers: "on",
          minimap: { enabled: false },
          padding: { top: 16, bottom: 16 },
          scrollBeyondLastLine: false,
          wordWrap: "on",
        }}
        theme="vs-dark"
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
  border: "1px solid #262b36",
  borderRadius: 16,
  background: "#12151c",
};

const statusBarStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 12,
  padding: "10px 14px",
  borderTop: "1px solid #262b36",
  background: "#10141b",
};

const statusTextStyle: CSSProperties = {
  color: "#9ba3b4",
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
