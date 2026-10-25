import { create } from "zustand";
import type {
  Draft,
  WorkspaceMode,
  CompileDraftResponse,
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
  lastCompileResult: CompileDraftResponse | null;
  activeBoundingBoxes: number[][]; // [[x0, y0, x1, y1, page], ...]
  activePage: number;
  previewPdfBlobUrl: string | null;
  assistantPrompt: string;
  isAssisting: boolean;
  selectionRange: { start: number; end: number } | null;
  isAssetModalOpen: boolean;
  isFileTreeOpen: boolean;
  activeSidebarTab: "files" | "outline";
  mobileActiveTab: "editor" | "preview" | "assistant";

  // Actions
  toggleFileTree: () => void;
  setFileTreeOpen: (open: boolean) => void;
  setActiveSidebarTab: (tab: "files" | "outline") => void;
  setMobileActiveTab: (tab: "editor" | "preview" | "assistant") => void;
  setDraft: (draft: Draft) => void;
  setEditorContent: (content: string) => void;
  setEditorTitle: (title: string) => void;
  setWorkspaceMode: (mode: WorkspaceMode) => void;
  setActiveBoundingBoxes: (boxes: number[][], page?: number) => void;
  setCompileResult: (result: CompileDraftResponse | null) => void;
  setPreviewPdfBlobUrl: (url: string | null) => void;
  setSaving: (saving: boolean) => void;
  setCompiling: (compiling: boolean) => void;
  setAssistantPrompt: (prompt: string) => void;
  setSelectionRange: (range: { start: number; end: number } | null) => void;
  setAssisting: (assisting: boolean) => void;
  openAssetModal: () => void;
  closeAssetModal: () => void;
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
  lastCompileResult: null,
  activeBoundingBoxes: [],
  activePage: 1,
  previewPdfBlobUrl: null,
  assistantPrompt: "",
  isAssisting: false,
  selectionRange: null,
  isAssetModalOpen: false,
  isFileTreeOpen: true,
  activeSidebarTab: "files",
  mobileActiveTab: "editor",

  toggleFileTree: () =>
    set((state) => ({ isFileTreeOpen: !state.isFileTreeOpen })),

  setFileTreeOpen: (isFileTreeOpen) => set({ isFileTreeOpen }),

  setActiveSidebarTab: (activeSidebarTab) => set({ activeSidebarTab }),

  setMobileActiveTab: (mobileActiveTab) => set({ mobileActiveTab }),

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

  setPreviewPdfBlobUrl: (previewPdfBlobUrl) => set({ previewPdfBlobUrl }),

  setSaving: (isSaving) => set({ isSaving }),

  setCompiling: (isCompiling) => set({ isCompiling }),

  setAssistantPrompt: (assistantPrompt) => set({ assistantPrompt }),

  setSelectionRange: (selectionRange) => set({ selectionRange }),

  setAssisting: (isAssisting) => set({ isAssisting }),

  openAssetModal: () => set({ isAssetModalOpen: true }),

  closeAssetModal: () => set({ isAssetModalOpen: false }),

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
      lastCompileResult: null,
      activeBoundingBoxes: [],
      activePage: 1,
      previewPdfBlobUrl: null,
      assistantPrompt: "",
      isAssisting: false,
      selectionRange: null,
      isAssetModalOpen: false,
      isFileTreeOpen: true,
      activeSidebarTab: "files",
      mobileActiveTab: "editor",
    }),
}));
