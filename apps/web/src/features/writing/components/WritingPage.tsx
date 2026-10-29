import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { WritingWorkspace } from "./WritingWorkspace";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { Loader2 } from "lucide-react";
import { STANDARD_ACADEMIC_LATEX_TEMPLATE } from "../constants/academicTemplate";

import { useDashboardSessions } from "@/features/dashboard/hooks/useDashboardSessions";

export function WritingPage() {
  const { draftId } = useParams<{ draftId?: string }>();
  const navigate = useNavigate();
  const { setDraft, activeDraftId } = useWritingStore();
  const { sessions } = useDashboardSessions();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function initDraft() {
      try {
        setLoading(true);
        if (draftId) {
          let draft = await draftsApi.getDraft(draftId);
          const isOldPlaceholder =
            !draft.content ||
            !draft.content.trim() ||
            draft.content.includes("Nội dung phần mở đầu giới thiệu bài toán nghiên cứu") ||
            !draft.content.includes("twocolumn");

          if (isOldPlaceholder) {
            draft = { ...draft, content: STANDARD_ACADEMIC_LATEX_TEMPLATE };
            draftsApi
              .updateDraft(draft.id, {
                title: draft.title,
                content: STANDARD_ACADEMIC_LATEX_TEMPLATE,
                format: draft.format,
                version: draft.version,
              })
              .then((updated) => {
                if (active) setDraft(updated);
              })
              .catch(() => {
                if (active) setDraft(draft);
              });
          } else if (active) {
            setDraft(draft);
          }
        } else {
          // Check for existing drafts or create a new one
          const listRes = await draftsApi.listDrafts(1, 1);
          if (listRes.data && listRes.data.length > 0) {
            let firstDraft = listRes.data[0];
            const isOldPlaceholder =
              !firstDraft.content ||
              !firstDraft.content.trim() ||
              firstDraft.content.includes("Nội dung phần mở đầu giới thiệu bài toán nghiên cứu") ||
              !firstDraft.content.includes("twocolumn");

            if (isOldPlaceholder) {
              firstDraft = { ...firstDraft, content: STANDARD_ACADEMIC_LATEX_TEMPLATE };
              draftsApi
                .updateDraft(firstDraft.id, {
                  title: firstDraft.title,
                  content: STANDARD_ACADEMIC_LATEX_TEMPLATE,
                  format: firstDraft.format,
                  version: firstDraft.version,
                })
                .then((updated) => {
                  if (active) setDraft(updated);
                })
                .catch(() => {
                  if (active) setDraft(firstDraft);
                });
            } else if (active) {
              setDraft(firstDraft);
            }
            if (active) {
              navigate(`/writing/${firstDraft.id}`, { replace: true });
            }
          } else {
            const created = await draftsApi.createDraft({
              title: "Nghiên Cứu Khoa Học Mới: Tiêu Đề Bài Báo",
              format: "latex",
              content: STANDARD_ACADEMIC_LATEX_TEMPLATE,
            });
            if (active) {
              setDraft(created);
              navigate(`/writing/${created.id}`, { replace: true });
            }
          }
        }
      } catch (err) {
        console.error("Failed to initialize draft:", err);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    initDraft();

    return () => {
      active = false;
    };
  }, [draftId, navigate, setDraft]);

  if (loading && !activeDraftId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center h-full w-full bg-canvas dark:bg-[#181715] text-ink dark:text-zinc-200">
        <Loader2 className="w-8 h-8 animate-spin text-coral-500 mb-2" />
        <p className="text-xs font-anthropic-serif">Đang nạp bản thảo...</p>
      </div>
    );
  }

  return <WritingWorkspace sessions={sessions} />;
}
