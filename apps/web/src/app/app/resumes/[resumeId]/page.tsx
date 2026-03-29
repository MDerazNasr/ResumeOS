import { notFound } from "next/navigation";
import { ResumeEditor } from "@/components/resumes/ResumeEditor";
import { getDraft, getResume } from "@/lib/api/client";

type ResumeEditorPageProps = {
  params: {
    resumeId: string;
  };
};

export default async function ResumeEditorPage({ params }: ResumeEditorPageProps) {
  try {
    const [resume, draft] = await Promise.all([getResume(params.resumeId), getDraft(params.resumeId)]);

    return (
      <main>
        <ResumeEditor draft={draft} resume={resume} />
      </main>
    );
  } catch {
    notFound();
  }
}

