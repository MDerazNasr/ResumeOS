export type UserDto = {
  id: string;
  email: string;
  name: string;
};

export type ResumeDto = {
  id: string;
  title: string;
  slug: string;
  status: "active" | "archived";
  createdAt: string;
  updatedAt: string;
};

export type ResumeListResponseDto = {
  items: ResumeDto[];
};

export type WorkingDraftDto = {
  resumeId: string;
  sourceTex: string;
  version: number;
  updatedAt: string;
};

export type CreateResumeInput = {
  title: string;
};

export type UpdateDraftInput = {
  sourceTex: string;
  version: number;
};

export type CompileRequestInput = {
  sourceTex: string;
  draftVersion: number;
};

export type CompileLogEntryDto = {
  level: "info" | "error";
  message: string;
  line: number | null;
};

export type CompileResultDto = {
  status: "success" | "error";
  draftVersion: number;
  logs: CompileLogEntryDto[];
  pdfUrl: string | null;
  compiledAt: string;
};
