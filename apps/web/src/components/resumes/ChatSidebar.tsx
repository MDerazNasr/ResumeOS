"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import { createChatMessageStream } from "@/lib/api/client";
import type { ChatMessageDto, PatchSetDto } from "@/lib/api/types";

type ChatSidebarProps = {
  initialMessages: ChatMessageDto[];
  onPatchSetsGenerated: (patchSets: PatchSetDto[]) => void;
  resumeId: string;
};

export function ChatSidebar({ initialMessages, onPatchSetsGenerated, resumeId }: ChatSidebarProps) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastIntent, setLastIntent] = useState<"question" | "edit" | "review" | "tailor" | null>(null);
  const [lastIntentSource, setLastIntentSource] = useState<"message" | "history" | null>(null);
  const [lastPatchSummary, setLastPatchSummary] = useState<string | null>(null);
  const [lastFeedbackSummary, setLastFeedbackSummary] = useState<string | null>(null);
  const [assistantTurnMeta, setAssistantTurnMeta] = useState<
    Record<string, { intent: "question" | "edit" | "review" | "tailor"; intentSource: "message" | "history"; summary: string | null; feedbackSummary: string | null }>
  >({});

  async function handleSend() {
    const content = input.trim();
    if (!content) {
      return;
    }

    const optimisticUserMessage: ChatMessageDto = {
      id: `optimistic-user-${Date.now()}`,
      role: "user",
      content,
      createdAt: new Date().toISOString(),
    };
    const optimisticAssistantMessage: ChatMessageDto = {
      id: `optimistic-assistant-${Date.now()}`,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
    };

    setIsSending(true);
    setError(null);
    setMessages((current) => [...current, optimisticUserMessage, optimisticAssistantMessage]);
    setInput("");

    try {
      await createChatMessageStream(resumeId, { content }, {
        onStart: ({ chatIntent, intentSource }) => {
          setLastIntent(chatIntent);
          setLastIntentSource(intentSource);
          setLastPatchSummary(null);
          setLastFeedbackSummary(null);
          setAssistantTurnMeta((current) => ({
            ...current,
            [optimisticAssistantMessage.id]: {
              intent: chatIntent,
              intentSource,
              summary: null,
              feedbackSummary: null,
            },
          }));
        },
        onDelta: (delta) => {
          setMessages((current) =>
            current.map((message) =>
              message.id === optimisticAssistantMessage.id
                ? { ...message, content: `${message.content}${delta}` }
                : message,
            ),
          );
        },
        onComplete: (response) => {
          setMessages(response.thread.messages);
          setLastIntent(response.chatIntent);
          setLastIntentSource(response.intentSource);
          setLastPatchSummary(response.generatedPatchSetSummary);
          setLastFeedbackSummary(response.recentFeedbackSummary);
          setAssistantTurnMeta((current) => {
            const next = { ...current };
            delete next[optimisticAssistantMessage.id];
            next[response.assistantMessageId] = {
              intent: response.chatIntent,
              intentSource: response.intentSource,
              summary: response.generatedPatchSetSummary,
              feedbackSummary: response.recentFeedbackSummary,
            };
            return next;
          });
          if (response.patchSets.length > 0) {
            onPatchSetsGenerated(response.patchSets);
          }
        },
      });
    } catch (sendError) {
      setMessages((current) =>
        current.filter(
          (message) => message.id !== optimisticUserMessage.id && message.id !== optimisticAssistantMessage.id,
        ),
      );
      setError(sendError instanceof Error ? sendError.message : "Failed to send chat message.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>AI Chat</strong>
        <span style={{ color: "var(--muted)", fontSize: 13 }}>
          Ask for review, improvement, or tailoring. Chat can hand patch sets back into the editor.
        </span>
      </div>
      <div style={messagesStyle}>
        {lastIntent ? (
          <div style={intentBannerStyle}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <span style={intentBadgeStyle(lastIntent)}>{lastIntent}</span>
              {lastIntentSource === "history" ? <span style={followUpBadgeStyle}>follow-up</span> : null}
            </div>
            <span style={{ color: "var(--muted)", fontSize: 12 }}>
              {lastPatchSummary ?? "This reply was informational only and did not load patch sets."}
            </span>
            {lastFeedbackSummary ? <span style={{ color: "var(--muted)", fontSize: 12 }}>Recent outcomes: {lastFeedbackSummary}</span> : null}
          </div>
        ) : null}
        {messages.length === 0 ? (
          <p style={{ margin: 0, color: "var(--muted)", lineHeight: 1.6 }}>
            Start with “Review my resume”, “Improve the wording”, or paste a job description and ask to tailor it.
          </p>
        ) : (
          messages.map((message) => (
            <div key={message.id} style={messageCardStyle(message.role)}>
              <strong style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em" }}>{message.role}</strong>
              {message.role === "assistant" && assistantTurnMeta[message.id] ? (
                <div style={messageMetaStyle}>
                  <strong style={{ fontSize: 13 }}>{assistantHeading(assistantTurnMeta[message.id].intent, assistantTurnMeta[message.id].summary)}</strong>
                  <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                    <span style={intentBadgeStyle(assistantTurnMeta[message.id].intent)}>{assistantTurnMeta[message.id].intent}</span>
                    {assistantTurnMeta[message.id].intentSource === "history" ? <span style={followUpBadgeStyle}>follow-up</span> : null}
                  </div>
                  <span style={{ color: "var(--muted)", fontSize: 12 }}>
                    {assistantTurnMeta[message.id].summary ?? "Informational reply only."}
                  </span>
                  {assistantTurnMeta[message.id].feedbackSummary ? (
                    <span style={{ color: "var(--muted)", fontSize: 12 }}>
                      Recent outcomes: {assistantTurnMeta[message.id].feedbackSummary}
                    </span>
                  ) : null}
                </div>
              ) : null}
              <p style={{ margin: 0, lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{message.content}</p>
            </div>
          ))
        )}
      </div>
      <textarea
        onChange={(event) => setInput(event.target.value)}
        placeholder="Ask the AI to review, improve, or tailor the resume..."
        style={inputStyle}
        value={input}
      />
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <span style={{ color: error ? "var(--diff-remove-fg)" : "var(--muted)", fontSize: 12 }}>
          {error ?? "Chat replies are grounded in the current draft, saved constraints, and patch workflow."}
        </span>
        <button disabled={isSending} onClick={() => void handleSend()} style={buttonStyle} type="button">
          {isSending ? "Sending..." : "Send"}
        </button>
      </div>
    </section>
  );
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 12,
  padding: 16,
  border: "1px solid var(--border)",
  borderRadius: 14,
  background: "var(--surface)",
};

const messagesStyle: CSSProperties = {
  display: "grid",
  gap: 10,
  maxHeight: 320,
  overflowY: "auto",
};

const intentBannerStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  padding: 10,
  border: "1px solid var(--border)",
  borderRadius: 12,
  background: "var(--surface-alt)",
};

function intentBadgeStyle(intent: "question" | "edit" | "review" | "tailor"): CSSProperties {
  return {
    width: "fit-content",
    padding: "4px 8px",
    borderRadius: 999,
    background:
      intent === "tailor"
        ? "var(--mode-tailor-bg, rgba(79, 124, 255, 0.15))"
        : intent === "review"
          ? "var(--mode-review-bg, rgba(102, 193, 140, 0.15))"
          : intent === "edit"
            ? "var(--badge-bg)"
            : "var(--surface-elevated)",
    color:
      intent === "tailor"
        ? "var(--mode-tailor-fg, #7db2ff)"
        : intent === "review"
          ? "var(--mode-review-fg, #9fe3b5)"
          : "var(--fg)",
    fontSize: 11,
    fontWeight: 700,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
  };
}

function messageCardStyle(role: "user" | "assistant"): CSSProperties {
  return {
    display: "grid",
    gap: 6,
    padding: 12,
    borderRadius: 12,
    border: `1px solid ${role === "assistant" ? "var(--border)" : "var(--border-strong)"}`,
    background: role === "assistant" ? "var(--surface-alt)" : "var(--surface-elevated)",
  };
}

function assistantHeading(
  intent: "question" | "edit" | "review" | "tailor",
  summary: string | null,
): string {
  if (!summary) {
    return intent === "question" ? "Resume Context Answer" : "No Patch Sets Generated";
  }

  if (intent === "review") {
    return "Review Patch Sets Ready";
  }

  if (intent === "tailor") {
    return "Tailoring Patch Sets Ready";
  }

  if (intent === "edit") {
    return "Edit Patch Sets Ready";
  }

  return "Resume Context Answer";
}

const messageMetaStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  padding: "8px 10px",
  borderRadius: 10,
  background: "var(--surface-elevated)",
};

const followUpBadgeStyle: CSSProperties = {
  width: "fit-content",
  padding: "4px 8px",
  borderRadius: 999,
  background: "var(--surface-elevated)",
  color: "var(--muted)",
  fontSize: 11,
  fontWeight: 700,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
};

const inputStyle: CSSProperties = {
  minHeight: 110,
  width: "100%",
  resize: "vertical",
  padding: 12,
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--surface-input)",
  color: "var(--fg)",
  font: "inherit",
  lineHeight: 1.5,
};

const buttonStyle: CSSProperties = {
  padding: "10px 14px",
  border: "1px solid var(--border-strong)",
  borderRadius: 12,
  background: "var(--surface)",
  color: "var(--fg)",
  cursor: "pointer",
};
