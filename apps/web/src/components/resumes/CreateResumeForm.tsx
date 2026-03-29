"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { createResume } from "@/lib/api/client";

export function CreateResumeForm() {
  const router = useRouter();
  const [title, setTitle] = useState("Master Resume");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const resume = await createResume({ title });
      router.push(`/app/resumes/${resume.id}`);
      router.refresh();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Failed to create resume.");
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <label style={labelStyle}>
        New Resume
        <input
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Master Resume"
          style={inputStyle}
          value={title}
        />
      </label>
      <button disabled={isSubmitting || title.trim().length === 0} style={buttonStyle} type="submit">
        {isSubmitting ? "Creating..." : "Create Resume"}
      </button>
      {error ? <p style={errorStyle}>{error}</p> : null}
    </form>
  );
}

const formStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  padding: 20,
  border: "1px solid #262b36",
  borderRadius: 16,
  background: "#171a21"
};

const labelStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  color: "#c8d0de",
  fontSize: 14
};

const inputStyle: CSSProperties = {
  width: "100%",
  padding: "12px 14px",
  border: "1px solid #313748",
  borderRadius: 12,
  background: "#0f1115",
  color: "#eef1f6"
};

const buttonStyle: CSSProperties = {
  width: "fit-content",
  padding: "10px 14px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#eef1f6",
  color: "#0f1115",
  cursor: "pointer"
};

const errorStyle: CSSProperties = {
  margin: 0,
  color: "#ff8d8d"
};
