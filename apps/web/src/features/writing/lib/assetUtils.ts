import type { DraftAsset } from "../types";

export function formatBytes(bytes: number, decimals = 1): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

export function generateLatexSnippet(asset: DraftAsset): string {
  const ext = asset.filename.split(".").pop()?.toLowerCase() || "";
  const nameWithoutExt = asset.filename.replace(/\.[^/.]+$/, "");
  const label = asset.latex_label || `fig:${nameWithoutExt}`;
  const caption = asset.caption || "Hình ảnh minh họa nghiên cứu";

  if (["png", "jpg", "jpeg", "webp"].includes(ext) || asset.asset_type === "image") {
    return `\\begin{figure}[htbp]
  \\centering
  \\includegraphics[width=0.8\\textwidth]{${asset.filename}}
  \\caption{${caption}}
  \\label{${label}}
\\end{figure}`;
  }

  if (ext === "bib" || asset.asset_type === "bibtex") {
    return `\\bibliographystyle{plain}
\\bibliography{${nameWithoutExt}}`;
  }

  if (ext === "cls") {
    return `\\documentclass{${nameWithoutExt}}`;
  }

  if (ext === "sty") {
    return `\\usepackage{${nameWithoutExt}}`;
  }

  if (ext === "pdf") {
    return `\\includegraphics[width=\\linewidth]{${asset.filename}}`;
  }

  return `\\input{${asset.filename}}`;
}
