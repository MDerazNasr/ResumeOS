import type {
  ApplyPatchInput,
  CompileRequestInput,
  CompileResultDto,
  CreateSnapshotInput,
  CreateResumeInput,
  DocumentModelDto,
  GenerateEditSuggestionsInput,
  GenerateReviewSuggestionsInput,
  GenerateTailorSuggestionsInput,
  LogFeedbackInput,
  MockSuggestionSetListDto,
  PatchSetListDto,
  RestoreSnapshotInput,
  ResumeDto,
  ResumeListResponseDto,
  SnapshotDetailDto,
  SnapshotDto,
  SnapshotListResponseDto,
  UpdateDraftInput,
  UserDto,
  WorkingDraftDto
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
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

export function getCurrentUser(): Promise<UserDto> {
  return apiFetch<UserDto>("/me");
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

export function getMockPatches(resumeId: string, seed = 0): Promise<MockSuggestionSetListDto> {
  return apiFetch<MockSuggestionSetListDto>(`/resumes/${resumeId}/patches/mock?seed=${seed}`);
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
): Promise<MockSuggestionSetListDto> {
  return apiFetch<MockSuggestionSetListDto>(`/resumes/${resumeId}/suggestions/review`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function generateTailorSuggestions(
  resumeId: string,
  input: GenerateTailorSuggestionsInput,
): Promise<MockSuggestionSetListDto> {
  return apiFetch<MockSuggestionSetListDto>(`/resumes/${resumeId}/suggestions/tailor`, {
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
