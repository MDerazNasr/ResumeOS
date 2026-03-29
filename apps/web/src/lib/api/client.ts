import type {
  CompileRequestInput,
  CompileResultDto,
  CreateResumeInput,
  ResumeDto,
  ResumeListResponseDto,
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
