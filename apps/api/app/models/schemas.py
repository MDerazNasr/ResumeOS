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
