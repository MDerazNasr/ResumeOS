import { notFound, redirect } from "next/navigation";
import { ResumeEditor } from "@/components/resumes/ResumeEditor";
import { getCurrentUser, getDocumentModel, getDraft, getResume, listSnapshots } from "@/lib/api/client";

type ResumeEditorPageProps = {
  params: {
    resumeId: string;
  };
};

export default async function ResumeEditorPage({ params }: ResumeEditorPageProps) {
  const user = await getCurrentUser();

  if (user.authSource !== "session") {
    redirect("/auth");
  }

  try {
    const [resume, draft, documentModel, snapshots] = await Promise.all([
      getResume(params.resumeId),
      getDraft(params.resumeId),
      getDocumentModel(params.resumeId),
      listSnapshots(params.resumeId),
    ]);

    return (
      <main>
        <ResumeEditor
          documentModel={documentModel}
          draft={draft}
          initialSnapshots={snapshots.items}
          resume={resume}
        />
      </main>
    );
  } catch {
    notFound();
  }
}
