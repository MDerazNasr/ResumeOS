from typing import Literal

from pydantic import BaseModel, Field


class UserDto(BaseModel):
    id: str
    email: str
    name: str


class GoogleAuthStatusDto(BaseModel):
    configured: bool


class UserSettingsDto(BaseModel):
    editorMode: Literal["standard", "vim"]
    themeMode: Literal["dark", "light"]


class UpdateUserSettingsInput(BaseModel):
    editorMode: Literal["standard", "vim"] | None = None
    themeMode: Literal["dark", "light"] | None = None


class ResumeDto(BaseModel):
    id: str
    title: str
    slug: str
    status: str
    createdAt: str
    updatedAt: str


class ResumeListResponseDto(BaseModel):
    items: list[ResumeDto]


class CreateResumeInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class WorkingDraftDto(BaseModel):
    resumeId: str
    sourceTex: str
    version: int
    updatedAt: str


class ProtectedRegionDto(BaseModel):
    id: str
    kind: Literal["preamble", "scaffold", "command"]
    label: str
    startLine: int
    endLine: int


class EditableBlockDto(BaseModel):
    id: str
    kind: Literal["paragraph", "bullet"]
    label: str
    text: str
    startLine: int
    startColumn: int
    endLine: int
    endColumn: int


class DocumentModelDto(BaseModel):
    resumeId: str
    protectedRegions: list[ProtectedRegionDto]
    editableBlocks: list[EditableBlockDto]


class ValidatePatchInput(BaseModel):
    targetBlockId: str
    startLine: int = Field(ge=1)
    endLine: int = Field(ge=1)
    beforeText: str


class PatchValidationResultDto(BaseModel):
    isValid: bool
    targetBlockId: str
    matchedCurrentText: str | None = None
    reason: str | None = None


class PatchHunkDto(BaseModel):
    id: str
    operation: Literal["replace"]
    status: Literal["validated"]
    targetBlockId: str
    label: str
    startLine: int
    endLine: int
    beforeText: str
    afterText: str
    rationale: str
    validation: PatchValidationResultDto


class PatchSetDto(BaseModel):
    id: str
    mode: Literal["mock", "edit", "review", "tailor"]
    title: str
    summary: str
    styleExamples: list[str] = []
    retrySeed: int
    items: list[PatchHunkDto]


class PatchSetListDto(BaseModel):
    items: list[PatchSetDto]


class LogFeedbackInput(BaseModel):
    suggestionMode: Literal["mock", "edit", "review", "tailor"]
    action: Literal["apply", "dismiss"]
    suggestionSetId: str
    proposalId: str
    targetBlockId: str


class ApplyPatchInput(BaseModel):
    targetBlockId: str
    startLine: int = Field(ge=1)
    endLine: int = Field(ge=1)
    beforeText: str
    afterText: str


class GenerateEditSuggestionsInput(BaseModel):
    targetBlockId: str
    instruction: str = Field(min_length=1, max_length=300)


class GenerateReviewSuggestionsInput(BaseModel):
    instruction: str = Field(min_length=1, max_length=300)


class GenerateTailorSuggestionsInput(BaseModel):
    jobDescription: str = Field(min_length=20, max_length=6000)
    instruction: str = Field(min_length=1, max_length=300)


class UpdateDraftInput(BaseModel):
    sourceTex: str
    version: int = Field(ge=1)


class CompileRequestInput(BaseModel):
    sourceTex: str
    draftVersion: int = Field(ge=1)


class CompileLogEntryDto(BaseModel):
    level: Literal["info", "error"]
    message: str
    line: int | None = None


class CompileResultDto(BaseModel):
    status: Literal["success", "error"]
    draftVersion: int
    logs: list[CompileLogEntryDto]
    pdfUrl: str | None = None
    compiledAt: str


class SnapshotDto(BaseModel):
    id: str
    resumeId: str
    name: str
    sourceVersion: int
    createdAt: str


class SnapshotDetailDto(SnapshotDto):
    sourceTex: str


class SnapshotListResponseDto(BaseModel):
    items: list[SnapshotDto]


class CreateSnapshotInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class RestoreSnapshotInput(BaseModel):
    snapshotId: str


class ChatMessageDto(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    createdAt: str


class ChatThreadDto(BaseModel):
    id: str
    resumeId: str
    messages: list[ChatMessageDto]


class CreateChatMessageInput(BaseModel):
    content: str = Field(min_length=1, max_length=6000)


class ChatResponseDto(BaseModel):
    thread: ChatThreadDto
    chatIntent: Literal["question", "edit", "review", "tailor"]
    generatedPatchSetSummary: str | None = None
    assistantMessageId: str
    patchSets: list[PatchSetDto] = []
