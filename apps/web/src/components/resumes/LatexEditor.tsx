"use client";

import dynamic from "next/dynamic";
import type { CSSProperties } from "react";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
});

type LatexEditorProps = {
  value: string;
  onChange: (value: string) => void;
};

export function LatexEditor({ value, onChange }: LatexEditorProps) {
  return (
    <div style={editorShellStyle}>
      <MonacoEditor
        defaultLanguage="latex"
        height="70vh"
        onChange={(nextValue) => onChange(nextValue ?? "")}
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
    </div>
  );
}

const editorShellStyle: CSSProperties = {
  overflow: "hidden",
  border: "1px solid #262b36",
  borderRadius: 16,
  background: "#12151c",
};
