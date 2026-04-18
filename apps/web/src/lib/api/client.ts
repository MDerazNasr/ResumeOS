import type {
  ApplyPatchInput,
  ChatResponseDto,
  ChatThreadDto,
  CompileRequestInput,
  CompileResultDto,
  CreateChatMessageInput,
  CreateSnapshotInput,
  CreateResumeInput,
  DocumentModelDto,
  GenerateEditSuggestionsInput,
  GenerateReviewSuggestionsInput,
  GenerateTailorSuggestionsInput,
  GoogleAuthStatusDto,
  HolisticReviewContextDto,
  LogFeedbackInput,
  PatchSetListDto,
  RestoreSnapshotInput,
  ResumeDto,
  ResumeListResponseDto,
  SnapshotDetailDto,
  SnapshotDto,
  SnapshotListResponseDto,
  UpdateDraftInput,
  UpdateUserSettingsInput,
  UserDto,
  UserSettingsDto,
  WorkingDraftDto
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const forwardedHeaders = await buildRequestHeaders(init?.headers);
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: forwardedHeaders,
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

async function buildRequestHeaders(initHeaders?: HeadersInit): Promise<HeadersInit> {
  const headers = new Headers(initHeaders);

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (typeof window === "undefined") {
    const { cookies } = await import("next/headers");
    const cookieStore = cookies();
    const cookieHeader = cookieStore.toString();

    if (cookieHeader && !headers.has("Cookie")) {
      headers.set("Cookie", cookieHeader);
    }
  }

  return headers;
}

export async function getCurrentUser(): Promise<UserDto | null> {
  try {
    return await apiFetch<UserDto>("/me");
  } catch (error) {
    if (error instanceof Error && error.message === "API request failed: 401") {
      return null;
    }
    throw error;
  }
}

export function getGoogleAuthStatus(): Promise<GoogleAuthStatusDto> {
  return apiFetch<GoogleAuthStatusDto>("/auth/google/status");
}

export function getGoogleAuthStartUrl(): string {
  return `${API_BASE_URL}/auth/google/start`;
}

export function logoutUser(): Promise<void> {
  return apiFetch<void>("/auth/logout", {
    method: "POST"
  });
}

export function getUserSettings(): Promise<UserSettingsDto> {
  return apiFetch<UserSettingsDto>("/settings");
}

export function updateUserSettings(input: UpdateUserSettingsInput): Promise<UserSettingsDto> {
  return apiFetch<UserSettingsDto>("/settings", {
    method: "PATCH",
    body: JSON.stringify(input)
  });
}

export function listResumes(): Promise<ResumeListResponseDto> {
  return apiFetch<ResumeListResponseDto>("/resumes");
}

export function createResume(input: CreateResumeInput): Promise<ResumeDto> {
  return apiFetch<ResumeDto>("/resumes", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getResume(resumeId: string): Promise<ResumeDto> {
  return apiFetch<ResumeDto>(`/resumes/${resumeId}`);
}

export function getDraft(resumeId: string): Promise<WorkingDraftDto> {
  return apiFetch<WorkingDraftDto>(`/resumes/${resumeId}/draft`);
}

export function getDocumentModel(resumeId: string): Promise<DocumentModelDto> {
  return apiFetch<DocumentModelDto>(`/resumes/${resumeId}/document-model`);
}

export function getHolisticReviewContext(resumeId: string): Promise<HolisticReviewContextDto> {
  return apiFetch<HolisticReviewContextDto>(`/resumes/${resumeId}/holistic-review/context`);
}

export function getSeededPatchSets(resumeId: string, seed = 0): Promise<PatchSetListDto> {
  return apiFetch<PatchSetListDto>(`/resumes/${resumeId}/patch-sets/seeded?seed=${seed}`);
}

export function generateEditSuggestions(
  resumeId: string,
  input: GenerateEditSuggestionsInput,
): Promise<PatchSetListDto> {
  return apiFetch<PatchSetListDto>(`/resumes/${resumeId}/suggestions/edit`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function generateReviewSuggestions(
  resumeId: string,
  input: GenerateReviewSuggestionsInput,
): Promise<PatchSetListDto> {
  return apiFetch<PatchSetListDto>(`/resumes/${resumeId}/suggestions/review`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function generateTailorSuggestions(
  resumeId: string,
  input: GenerateTailorSuggestionsInput,
): Promise<PatchSetListDto> {
  return apiFetch<PatchSetListDto>(`/resumes/${resumeId}/suggestions/tailor`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function applyPatch(resumeId: string, input: ApplyPatchInput): Promise<WorkingDraftDto> {
  return apiFetch<WorkingDraftDto>(`/resumes/${resumeId}/patches/apply`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function logFeedback(resumeId: string, input: LogFeedbackInput): Promise<void> {
  return apiFetch<void>(`/resumes/${resumeId}/feedback`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function saveDraft(resumeId: string, input: UpdateDraftInput): Promise<WorkingDraftDto> {
  return apiFetch<WorkingDraftDto>(`/resumes/${resumeId}/draft`, {
    method: "PUT",
    body: JSON.stringify(input)
  });
}

export function compileDraft(resumeId: string, input: CompileRequestInput): Promise<CompileResultDto> {
  return apiFetch<CompileResultDto>(`/resumes/${resumeId}/compile`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function listSnapshots(resumeId: string): Promise<SnapshotListResponseDto> {
  return apiFetch<SnapshotListResponseDto>(`/resumes/${resumeId}/snapshots`);
}

export function createSnapshot(resumeId: string, input: CreateSnapshotInput): Promise<SnapshotDto> {
  return apiFetch<SnapshotDto>(`/resumes/${resumeId}/snapshots`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getSnapshot(resumeId: string, snapshotId: string): Promise<SnapshotDetailDto> {
  return apiFetch<SnapshotDetailDto>(`/resumes/${resumeId}/snapshots/${snapshotId}`);
}

export function restoreSnapshot(resumeId: string, input: RestoreSnapshotInput): Promise<WorkingDraftDto> {
  return apiFetch<WorkingDraftDto>(`/resumes/${resumeId}/snapshots/restore`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getChatThread(resumeId: string): Promise<ChatThreadDto> {
  return apiFetch<ChatThreadDto>(`/resumes/${resumeId}/chat`);
}

export function createChatMessage(resumeId: string, input: CreateChatMessageInput): Promise<ChatResponseDto> {
  return apiFetch<ChatResponseDto>(`/resumes/${resumeId}/chat/messages`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export async function createChatMessageStream(
  resumeId: string,
  input: CreateChatMessageInput,
  handlers: {
    onStart?: (meta: { chatIntent: "question" | "edit" | "review" | "tailor"; intentSource: "message" | "history" }) => void;
    onDelta?: (delta: string) => void;
    onComplete: (response: ChatResponseDto) => void;
  }
): Promise<void> {
  const headers = await buildRequestHeaders();
  const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}/chat/messages/stream`, {
    method: "POST",
    credentials: "include",
    headers,
    body: JSON.stringify(input),
    cache: "no-store"
  });

  if (!response.ok || !response.body) {
    throw new Error(`API request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) {
        continue;
      }

      const event = JSON.parse(line) as
        | { type: "start"; chatIntent: "question" | "edit" | "review" | "tailor"; intentSource: "message" | "history" }
        | { type: "delta"; delta: string }
        | { type: "complete"; response: ChatResponseDto };

      if (event.type === "start") {
        handlers.onStart?.({ chatIntent: event.chatIntent, intentSource: event.intentSource });
      } else if (event.type === "delta") {
        handlers.onDelta?.(event.delta);
      } else if (event.type === "complete") {
        handlers.onComplete(event.response);
      }
    }
  }
}
