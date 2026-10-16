import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { WritingWorkspace } from "./WritingWorkspace";
import { useWritingStore } from "../stores/useWritingStore";
import { draftsApi } from "../api/draftsApi";
import { Loader2 } from "lucide-react";

export function WritingPage() {
  const { draftId } = useParams<{ draftId?: string }>();
  const navigate = useNavigate();
  const { setDraft, activeDraftId } = useWritingStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function initDraft() {
      try {
        setLoading(true);
        if (draftId) {
          const draft = await draftsApi.getDraft(draftId);
          if (active) {
            setDraft(draft);
          }
        } else {
          // Check for existing drafts or create a new one
          const listRes = await draftsApi.listDrafts(1, 1);
          if (listRes.data && listRes.data.length > 0) {
            const firstDraft = listRes.data[0];
            if (active) {
              setDraft(firstDraft);
              navigate(`/writing/${firstDraft.id}`, { replace: true });
            }
          } else {
            const created = await draftsApi.createDraft({
              title: "Untitled Research Draft",
              format: "latex",
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
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-canvas dark:bg-[#181715] text-ink dark:text-zinc-200">
        <Loader2 className="w-8 h-8 animate-spin text-coral-500 mb-2" />
        <p className="text-xs font-anthropic-serif">Đang nạp không gian soạn thảo học thuật...</p>
      </div>
    );
  }

  return <WritingWorkspace />;
}
