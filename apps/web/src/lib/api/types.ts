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

export type ProtectedRegionDto = {
  id: string;
  kind: "preamble" | "scaffold" | "command";
  label: string;
  startLine: number;
  endLine: number;
};

export type EditableBlockDto = {
  id: string;
  kind: "paragraph" | "bullet";
  label: string;
  text: string;
  startLine: number;
  startColumn: number;
  endLine: number;
  endColumn: number;
};

export type DocumentModelDto = {
  resumeId: string;
  protectedRegions: ProtectedRegionDto[];
  editableBlocks: EditableBlockDto[];
};

export type PatchValidationResultDto = {
  isValid: boolean;
  targetBlockId: string;
  matchedCurrentText: string | null;
  reason: string | null;
};

export type MockPatchProposalDto = {
  id: string;
  operation: "replace";
  status: "validated";
  targetBlockId: string;
  label: string;
  startLine: number;
  endLine: number;
  beforeText: string;
  afterText: string;
  rationale: string;
  validation: PatchValidationResultDto;
};

export type MockSuggestionSetDto = {
  id: string;
  mode: "mock" | "edit" | "review" | "tailor";
  title: string;
  summary: string;
  retrySeed: number;
  items: MockPatchProposalDto[];
};

export type MockSuggestionSetListDto = {
  items: MockSuggestionSetDto[];
};

export type ApplyPatchInput = {
  targetBlockId: string;
  startLine: number;
  endLine: number;
  beforeText: string;
  afterText: string;
};

export type GenerateEditSuggestionsInput = {
  targetBlockId: string;
  instruction: string;
};

export type GenerateReviewSuggestionsInput = {
  instruction: string;
};

export type GenerateTailorSuggestionsInput = {
  jobDescription: string;
  instruction: string;
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

export type SnapshotDto = {
  id: string;
  resumeId: string;
  name: string;
  sourceVersion: number;
  createdAt: string;
};

export type SnapshotDetailDto = SnapshotDto & {
  sourceTex: string;
};

export type SnapshotListResponseDto = {
  items: SnapshotDto[];
};

export type CreateSnapshotInput = {
  name: string;
};

export type RestoreSnapshotInput = {
  snapshotId: string;
};
