export const STANDARD_ACADEMIC_LATEX_TEMPLATE = `\\documentclass[10pt,twocolumn,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[top=2.2cm,bottom=2.2cm,left=1.8cm,right=1.8cm,columnsep=0.8cm]{geometry}
\\usepackage{amsmath,amsfonts,amssymb}
\\usepackage{graphicx}
\\usepackage{booktabs}
\\usepackage{xcolor}
\\usepackage{microtype}
\\usepackage{hyperref}

\\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=teal,
    urlcolor=blue
}

\\title{\\textbf{\\Large KIẾN TRÚC MÔ HÌNH SOCRATIC COPILOT: \\\\ TỰ ĐỘNG PHẢN BIỆN VÀ ĐỐI CHIẾU DẪN CHỨNG HỌC THUẬT}}
\\author{
  \\textbf{Học giả VeriScholar}$^{1,2}$, \\textbf{Ban Nghiên cứu Khoa học}$^{1}$ \\\\
  $^{1}$Viện Trí tuệ Nhân tạo Tiên tiến, Đại học Quốc gia \\\\
  $^{2}$Phòng Thí nghiệm Khoa học Dữ liệu \\& Hệ thống Phân tán \\\\
  \\texttt{\\{scholar, research\\}@verischolar.org}
}
\\date{\\today}

\\begin{document}

\\twocolumn[
  \\begin{@twocolumnfalse}
    \\maketitle
    \\begin{abstract}
    \\noindent
    Nghiên cứu này đề xuất kiến trúc \\textbf{Socratic Copilot}—hệ thống trợ lý học thuật thông minh thế hệ mới kết hợp mô hình suy luận đa bước (\\textit{Multi-step Reasoning}) và cơ chế đối chiếu dẫn chứng không gian hai chiều (\\textit{2D Bounding Box Verification}). Khác với các mô hình sinh văn bản thông thường dễ mắc lỗi ảo giác (\\textit{hallucination}), hệ thống của chúng tôi bám sát từng đoạn trích từ bài báo gốc, tự động phát hiện tiền đề sai lệch và cung cấp bảo chứng minh bạch đến từng tọa độ trang tài liệu. Thực nghiệm trên 1.000 bài báo khoa học chuẩn mực cho thấy phương pháp đạt độ chính xác 95.8\\% và giảm thiểu tỷ lệ ảo giác xuống dưới 0.7\\%.
    \\vspace{0.8em}
    
    \\noindent
    \\textbf{Từ khóa:} Socratic Copilot, Kiểm chứng trích dẫn, Phản biện học thuật, Bounding Box, Không ảo giác, Trí tuệ nhân tạo.
    \\vspace{1.2em}
    \\end{abstract}
  \\end{@twocolumnfalse}
]

\\section{Giới thiệu (Introduction)}
Trong kỷ nguyên bùng nổ của xuất bản khoa học, việc nắm bắt và thẩm định tính xác thực của các bài báo đặt ra thách thức lớn cho cộng đồng nghiên cứu quốc tế \\cite{vaswani2017}. Các mô hình ngôn ngữ lớn (LLMs) tuy có khả năng tóm tắt nhanh nhưng thường xuyên mắc lỗi bịa đặt trích dẫn (\\textit{citation hallucination}) và không thể chỉ ra được vị trí chính xác của dữ liệu trong văn bản gốc \\cite{devlin2018}.

Để giải quyết triệt để vấn đề này, bài báo giới thiệu mô hình Socratic Copilot với ba đóng góp cốt lõi:
\\begin{enumerate}
  \\item \\textbf{Cơ chế truy xuất đa tầng:} Kết hợp Content-Addressable Storage (CAS) và giải thuật bóc tách tọa độ không gian chính xác ($x_0, y_0, x_1, y_1, \\text{page}$).
  \\item \\textbf{Thuật toán phản biện Socrates:} Tự động phân tích các tiền đề ngụy biện trong câu hỏi của người dùng và hướng dẫn đối chiếu trực tiếp với bài báo.
  \\item \\textbf{Không gian soạn thảo Overleaf:} Tích hợp quy trình biên dịch \\LaTeX{} song song với đồng bộ hóa thời gian thực và kiểm chứng sự thật SAFE Fact-Checking.
\\end{enumerate}

\\section{Phương pháp Nghiên cứu (Methodology)}
Hệ thống mô hình hóa quá trình phản biện khoa học như một bài toán tối ưu hóa đa mục tiêu giữa tính trung thực của bằng chứng (\\textit{Faithfulness}) và độ sâu sắc của phản biện (\\textit{Critique Depth}):

\\begin{equation}
\\mathcal{L}_{\\text{total}} = \\alpha \\mathcal{L}_{\\text{faith}}(E, C) + \\beta \\mathcal{L}_{\\text{crit}}(Q, P) - \\gamma \\mathcal{R}_{\\text{halluc}}
\\end{equation}

\\noindent
Trong đó $E$ là tập các đoạn trích dẫn chứng (evidence chunks), $C$ là luận điểm được đưa ra (claim), và $Q$ là câu hỏi của nhà nghiên cứu.

Cơ chế phân giải trích dẫn được chuẩn hóa thông qua hàm ánh xạ tọa độ không gian:
\\begin{equation}
\\mathbf{B}(c) = [x_{\\min}, y_{\\min}, x_{\\max}, y_{\\max}, p] \\in \\mathbb{R}^4 \\times \\mathbb{N}^+
\\end{equation}

\\section{Kết quả Thực nghiệm (Results)}
Chúng tôi tiến hành thử nghiệm toàn diện trên tập dữ liệu gồm 1.000 bài báo khoa học chất lượng cao. Kết quả so sánh định lượng được thể hiện chi tiết tại Bảng~\\ref{tab:benchmark}.

\\begin{table}[htbp]
\\centering
\\caption{Đánh giá định lượng hiệu năng và độ tin cậy trích dẫn}
\\label{tab:benchmark}
\\vspace{0.4em}
\\resizebox{\\columnwidth}{!}{%
\\begin{tabular}{lcccc}
\\toprule
\\textbf{Phương pháp} & \\textbf{Độ chính xác} & \\textbf{F1} & \\textbf{Ảo giác} & \\textbf{Thời gian} \\\\
\\midrule
Vanilla LLM          & 71.4\\% & 0.68 & 19.8\\% & 1.25s \\\\
Standard RAG         & 82.6\\% & 0.81 & 8.4\\%  & 1.84s \\\\
CoT Reasoning        & 87.2\\% & 0.86 & 4.9\\%  & 2.45s \\\\
\\textbf{VeriScholar} & \\textbf{95.8\\%} & \\textbf{0.95} & \\textbf{0.7\\%} & \\textbf{0.92s} \\\\
\\bottomrule
\\end{tabular}%
}
\\end{table}

\\section{Thảo luận (Discussion)}
Kết quả cho thấy việc hiển thị Bounding Box trực quan kết hợp với phản biện Socrates giúp tăng 42\\% độ tin cậy của nhà nghiên cứu đối với các câu trả lời do AI tổng hợp, đồng thời loại bỏ hoàn toàn hiện tượng dẫn chứng sai nguồn.

\\section{Kết luận (Conclusion)}
Hệ thống VeriScholar thiết lập chuẩn mực mới cho công cụ hỗ trợ nghiên cứu khoa học: minh bạch, chính xác và có thể đối chứng tức thì.

\\begin{thebibliography}{9}
\\bibitem{vaswani2017}
A. Vaswani et al., \`\`Attention is all you need,'' in \\textit{NeurIPS}, 2017, pp. 5998--6008.

\\bibitem{devlin2018}
J. Devlin et al., \`\`BERT: Pre-training of deep bidirectional transformers,'' \\textit{arXiv:1810.04805}, 2018.
\\end{thebibliography}

\\end{document}
`;
