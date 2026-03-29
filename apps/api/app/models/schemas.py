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

