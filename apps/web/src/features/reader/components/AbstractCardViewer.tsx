import { AbstractOnlyViewer } from "./AbstractOnlyViewer";
import type { DocumentDetailResponseData } from "@/types/document";

export interface AbstractCardViewerProps {
  document: DocumentDetailResponseData;
  onPdfAttached?: () => void;
}

export function AbstractCardViewer(props: AbstractCardViewerProps) {
  return (
    <div data-testid="abstract-card-viewer" className="w-full h-full flex flex-col">
      <AbstractOnlyViewer {...props} />
    </div>
  );
}

export default AbstractCardViewer;
