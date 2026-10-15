import { create } from "zustand";
import type {
  Draft,
  WorkspaceMode,
  CompileDraftResponse,
  VerifyFactsResponse,
  AtomicClaim,
  PendingSuggestion,
} from "../types";

interface WritingState {
  activeDraftId?: string;
  draft: Draft | null;
  editorContent: string;
  editorTitle: string;
  workspaceMode: WorkspaceMode;
  isDirty: boolean;
  isSaving: boolean;
  isCompiling: boolean;
  isVerifying: boolean;
  lastCompileResult: CompileDraftResponse | null;
  lastVerifyResult: VerifyFactsResponse | null;
  activeBoundingBoxes: number[][]; // [[x0, y0, x1, y1, page], ...]
  activePage: number;
  previewPdfBlobUrl: string | null;
  selectedEvidenceClaim: AtomicClaim | null;
  isEvidenceModalOpen: boolean;
  assistantPrompt: string;
  pendingSuggestion: PendingSuggestion | null;
  isSuggestionPanelOpen: boolean;
  isAssisting: boolean;
  selectionRange: { start: number; end: number } | null;
  isAssetModalOpen: boolean;
  isShareModalOpen: boolean;

  // Actions
  setDraft: (draft: Draft) => void;
  setEditorContent: (content: string) => void;
  setEditorTitle: (title: string) => void;
  setWorkspaceMode: (mode: WorkspaceMode) => void;
  setActiveBoundingBoxes: (boxes: number[][], page?: number) => void;
  setCompileResult: (result: CompileDraftResponse | null) => void;
  setVerifyResult: (result: VerifyFactsResponse | null) => void;
  setPreviewPdfBlobUrl: (url: string | null) => void;
  setSaving: (saving: boolean) => void;
  setCompiling: (compiling: boolean) => void;
  setVerifying: (verifying: boolean) => void;
  openEvidenceModal: (claim: AtomicClaim) => void;
  closeEvidenceModal: () => void;
  setAssistantPrompt: (prompt: string) => void;
  setSelectionRange: (range: { start: number; end: number } | null) => void;
  openSuggestionPanel: (suggestion: PendingSuggestion) => void;
  closeSuggestionPanel: () => void;
  setAssisting: (assisting: boolean) => void;
  openAssetModal: () => void;
  closeAssetModal: () => void;
  openShareModal: () => void;
  closeShareModal: () => void;
  markSaved: (updatedDraft: Draft) => void;
  reset: () => void;
}

const DEFAULT_LATEX_CONTENT = `\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{graphicx}

\\title{VeriScholar Academic Paper}
\\author{Research Team}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
This paper presents a grounded study on verified academic claims and reproducible literature synthesis.
\\end{abstract}

\\section{Introduction}
Recent developments in transformer architectures have advanced natural language understanding.
As demonstrated by \\cite{vaswani2017attention}, the self-attention mechanism enables fast sequence modeling.

\\section{Related Work}
Previous methods relied heavily on recurrent networks, which suffered from sequential computation bottlenecks.

\\section{Methodology}
We evaluate factual consistency through Search-Augmented Factuality Evaluation (SAFE).

\\section{Conclusion}
Verifiable evidence grounding improves research synthesis fidelity.

\\bibliographystyle{plain}
\\bibliography{references}

\\end{document}
`;

export const useWritingStore = create<WritingState>((set) => ({
  activeDraftId: undefined,
  draft: null,
  editorContent: DEFAULT_LATEX_CONTENT,
  editorTitle: "Untitled Draft",
  workspaceMode: "tri-pane",
  isDirty: false,
  isSaving: false,
  isCompiling: false,
  isVerifying: false,
  lastCompileResult: null,
  lastVerifyResult: null,
  activeBoundingBoxes: [],
  activePage: 1,
  previewPdfBlobUrl: null,
  selectedEvidenceClaim: null,
  isEvidenceModalOpen: false,
  assistantPrompt: "",
  pendingSuggestion: null,
  isSuggestionPanelOpen: false,
  isAssisting: false,
  selectionRange: null,
  isAssetModalOpen: false,
  isShareModalOpen: false,

  setDraft: (draft) =>
    set({
      activeDraftId: draft.id,
      draft,
      editorContent: draft.content,
      editorTitle: draft.title,
      isDirty: false,
    }),

  setEditorContent: (editorContent) =>
    set({
      editorContent,
      isDirty: true,
    }),

  setEditorTitle: (editorTitle) =>
    set({
      editorTitle,
      isDirty: true,
    }),

  setWorkspaceMode: (workspaceMode) => set({ workspaceMode }),

  setActiveBoundingBoxes: (activeBoundingBoxes, page) =>
    set((state) => ({
      activeBoundingBoxes,
      activePage: page !== undefined ? page : state.activePage,
    })),

  setCompileResult: (lastCompileResult) => set({ lastCompileResult }),

  setVerifyResult: (lastVerifyResult) => set({ lastVerifyResult }),

  setPreviewPdfBlobUrl: (previewPdfBlobUrl) => set({ previewPdfBlobUrl }),

  setSaving: (isSaving) => set({ isSaving }),

  setCompiling: (isCompiling) => set({ isCompiling }),

  setVerifying: (isVerifying) => set({ isVerifying }),

  openEvidenceModal: (selectedEvidenceClaim) =>
    set((state) => ({
      selectedEvidenceClaim,
      isEvidenceModalOpen: true,
      activeBoundingBoxes: selectedEvidenceClaim.evidence_bounding_boxes || [],
      activePage:
        selectedEvidenceClaim.evidence_page !== undefined
          ? selectedEvidenceClaim.evidence_page
          : state.activePage,
    })),

  closeEvidenceModal: () =>
    set({
      isEvidenceModalOpen: false,
      selectedEvidenceClaim: null,
    }),

  setAssistantPrompt: (assistantPrompt) => set({ assistantPrompt }),

  setSelectionRange: (selectionRange) => set({ selectionRange }),

  openSuggestionPanel: (pendingSuggestion) =>
    set({ pendingSuggestion, isSuggestionPanelOpen: true }),

  closeSuggestionPanel: () =>
    set({ isSuggestionPanelOpen: false, pendingSuggestion: null }),

  setAssisting: (isAssisting) => set({ isAssisting }),

  openAssetModal: () => set({ isAssetModalOpen: true }),

  closeAssetModal: () => set({ isAssetModalOpen: false }),

  openShareModal: () => set({ isShareModalOpen: true }),

  closeShareModal: () => set({ isShareModalOpen: false }),

  markSaved: (updatedDraft) =>
    set({
      draft: updatedDraft,
      activeDraftId: updatedDraft.id,
      editorTitle: updatedDraft.title,
      editorContent: updatedDraft.content,
      isDirty: false,
      isSaving: false,
    }),

  reset: () =>
    set({
      activeDraftId: undefined,
      draft: null,
      editorContent: DEFAULT_LATEX_CONTENT,
      editorTitle: "Untitled Draft",
      workspaceMode: "tri-pane",
      isDirty: false,
      isSaving: false,
      isCompiling: false,
      isVerifying: false,
      lastCompileResult: null,
      lastVerifyResult: null,
      activeBoundingBoxes: [],
      activePage: 1,
      previewPdfBlobUrl: null,
      selectedEvidenceClaim: null,
      isEvidenceModalOpen: false,
      assistantPrompt: "",
      pendingSuggestion: null,
      isSuggestionPanelOpen: false,
      isAssisting: false,
      selectionRange: null,
      isAssetModalOpen: false,
      isShareModalOpen: false,
    }),
}));
