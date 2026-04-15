# Section 11: Chat Layer

## Goal

Add a persistent chat workflow that can discuss the resume and generate patch sets through the existing validated review system.

## Scope

- persistent per-resume chat thread
- visible chat sidebar in the editor workspace
- assistant replies grounded in the current draft
- chat-triggered patch-set generation for review/tailor intents
- short follow-up turns can inherit the last actionable chat intent
- chat replies should format differently for question, review, edit, and tailor modes
- chat transport should support incremental assistant rendering

## Out of Scope

- streaming chat transport
- full long-term conversation memory
- PDF-aware review
- direct document mutation from chat

## Implementation Checklist

- [x] define the Section 11 chat boundary
- [x] add backend chat thread/message persistence
- [x] add chat routes for listing the thread and sending a message
- [x] add a chat sidebar to the editor workspace
- [x] allow chat responses to return patch sets into the existing review flow
- [x] ground chat replies in recent thread history and style memory
- [x] route assistant replies through the provider abstraction
- [x] inherit actionable intent from recent chat history for clear follow-up turns
- [x] format assistant replies and chat cards by intent type
- [x] add transport-level chat streaming for incremental assistant rendering
- [x] verify backend tests pass
- [x] verify frontend production build passes

## Verification Checklist

- [x] backend tests pass
- [x] frontend production build passes
- [x] chat thread persists by resume
- [x] a chat message returns both stored messages and an assistant response
- [x] chat can load patch sets into the current review workflow
- [x] assistant replies record per-turn patch-set outcomes
- [x] clear follow-up turns can reuse the last actionable intent
- [x] assistant responses render with clearer mode-specific headings
- [x] chat stream endpoint emits start, delta, and complete events
