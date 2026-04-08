from typing import Literal

from pydantic import BaseModel, Field


class UserDto(BaseModel):
    id: str
    email: str
    name: str


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


class MockPatchProposalDto(BaseModel):
    id: str
    targetBlockId: str
    label: str
    startLine: int
    endLine: int
    beforeText: str
    afterText: str
    rationale: str
    validation: PatchValidationResultDto


class MockPatchProposalListDto(BaseModel):
    items: list[MockPatchProposalDto]


class ApplyPatchInput(BaseModel):
    targetBlockId: str
    startLine: int = Field(ge=1)
    endLine: int = Field(ge=1)
    beforeText: str
    afterText: str


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
