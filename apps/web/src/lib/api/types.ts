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

