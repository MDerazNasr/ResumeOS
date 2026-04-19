import { notFound, redirect } from "next/navigation";
import { ResumeEditor } from "@/components/resumes/ResumeEditor";
import { getChatThread, getCurrentUser, getDocumentModel, getDraft, getHolisticReviewContext, getResume, getResumeConstraints, listSnapshots } from "@/lib/api/client";

type ResumeEditorPageProps = {
  params: {
    resumeId: string;
  };
};

export default async function ResumeEditorPage({ params }: ResumeEditorPageProps) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/auth");
  }

  try {
    const [resume, draft, documentModel, constraints, holisticReviewContext, snapshots, chatThread] = await Promise.all([
      getResume(params.resumeId),
      getDraft(params.resumeId),
      getDocumentModel(params.resumeId),
      getResumeConstraints(params.resumeId),
      getHolisticReviewContext(params.resumeId),
      listSnapshots(params.resumeId),
      getChatThread(params.resumeId),
    ]);

    return (
      <main>
        <ResumeEditor
          constraints={constraints}
          documentModel={documentModel}
          draft={draft}
          holisticReviewContext={holisticReviewContext}
          initialChatMessages={chatThread.messages}
          initialSnapshots={snapshots.items}
          resume={resume}
        />
      </main>
    );
  } catch {
    notFound();
  }
}
