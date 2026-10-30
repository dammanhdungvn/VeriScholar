"""Compiled Academic Wiki Pages & Research Gaps data definitions (Spec 05)."""

from __future__ import annotations

from typing import Any

LANDMARK_WIKI_PAGES: list[dict[str, Any]] = [
    {
        "slug": "attention-is-all-you-need",
        "title": "Attention Is All You Need",
        "page_type": "topic",
        "wikilinks": [
            "transformer",
            "scaled-dot-product-attention",
            "multi-head-attention",
            "bert",
            "gpt-3",
            "lora",
        ],
        "yaml_metadata": {
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
            "year": 2017,
            "doi": "10.48550/arXiv.1706.03762",
            "summary": (
                "Đặt nền móng cho kiến trúc Transformer dựa trên cơ chế Attention. "
            ).strip(),
            "citations_count": 120000,
        },
        "markdown_content": "\n".join(
            [
                "# Attention Is All You Need (Vaswani et al., 2017)",
                "",
                "Bài báo kinh điển giới thiệu kiến trúc [[transformer]], một mô",
                "hình biến đổi chuỗi dựa",
                "hoàn toàn trên cơ chế self-attention, loại bỏ hoàn toàn các cấu",
                "trúc hồi quy (RNN/LSTM)",
                "và tích chập (CNN).",
                "",
                "## 1. Đóng góp cốt lõi",
                "- Đề xuất cơ chế [[scaled-dot-product-attention]] với công thức",
                "chuẩn hóa phân tán:",
                "",
                "922233  ext{Attention}(Q, K, V) =       ext{softmax}\\left(",
                "rac{QK^T}{\\sqrt{d_k}} ight)V922233",
                "",
                "- Thiết kế [[multi-head-attention]] cho phép mô hình đồng thời",
                "khai thác thông tin",
                "từ các không gian biểu diễn khác nhau.",
                "- Giảm thiểu độ trễ tính toán song song so với mạng nơ-ron hồi",
                "quy truyền thống.",
                "",
                "## 2. Liên kết học thuật",
                "- Phát triển nền tảng cho [[bert]], [[gpt-3]] và [[llama]].",
                "- Cơ sở cho các kỹ thuật tinh chỉnh tham số hiệu quả như [[lora]].",
                "",
            ]
        ),
    },
    {
        "slug": "transformer",
        "title": "Kiến trúc Transformer",
        "page_type": "method",
        "wikilinks": [
            "attention-is-all-you-need",
            "scaled-dot-product-attention",
            "multi-head-attention",
            "bert",
            "gpt-3",
            "llama",
        ],
        "yaml_metadata": {
            "summary": (
                "Mô hình học sâu dạng Encoder-Decoder dựa hoàn toàn trên self- attention. "
            ).strip(),
            "category": "Neural Architecture",
        },
        "markdown_content": "\n".join(
            [
                "# Kiến trúc Transformer",
                "",
                "Transformer là kiến trúc học sâu dạng bộ mã hóa - giải mã",
                "(Encoder-Decoder) dựa hoàn toàn trên",
                "[[attention-is-all-you-need|cơ chế tự chú ý]], thiết lập nền móng",
                "cho toàn bộ kỷ nguyên",
                "Mô hình Ngôn ngữ Lớn (LLM).",
                "",
                "## 1. Cấu trúc khối (Block Architecture)",
                "Mỗi khối gồm 2 tầng con chính:",
                "1. **[[multi-head-attention]]**: Nắm bắt tương quan ngữ nghĩa",
                "toàn cục giữa mọi cặp vị trí.",
                "2. **Feed-Forward Network (FFN)**: Biến đổi phi tuyến độc lập tại",
                "từng vị trí:",
                "",
                "922233\text{FFN}(x) = \\max(0, xW_1 + b_1)W_2 + b_2922233",
                "",
                "Đi kèm kết nối tắt (Residual Connection) và Chuẩn hóa tầng (Layer",
                "Normalization).",
                "",
                "## 2. Các biến thể tiếp nối",
                "- [[bert]]: Bộ mã hóa hai chiều (Bidirectional Encoder).",
                "- [[gpt-3]]: Mô hình tự hồi quy chỉ giải mã (Decoder-only",
                "Autoregressive).",
                "- [[llama]]: Kiến trúc mã nguồn mở chuẩn mực với RMSNorm và RoPE.",
                "",
            ]
        ),
    },
    {
        "slug": "scaled-dot-product-attention",
        "title": "Scaled Dot-Product Attention",
        "page_type": "method",
        "wikilinks": ["transformer", "multi-head-attention", "quadratic-memory-bottleneck"],
        "yaml_metadata": {
            "summary": (
                "Cơ chế chú ý tính tích vô hướng thu phóng theo căn bậc hai của d_k. "
            ).strip(),
            "complexity": "O(N^2)",
        },
        "markdown_content": "\n".join(
            [
                "# Scaled Dot-Product Attention",
                "",
                "Cơ chế tính toán trọng số tương quan giữa vector Query ($) và Key",
                "($), sau đó dùng",
                "phân phối xác suất Softmax để lấy trung bình có trọng số của các",
                "vector Value ($).",
                "",
                "## 1. Công thức toán học",
                "",
                "922233  ext{Attention}(Q, K, V) =       ext{softmax}\\left(",
                "rac{QK^T}{\\sqrt{d_k}} ight)V922233",
                "",
                "Trong đó thừa số $ rac{1}{\\sqrt{d_k}}$ đóng vai trò rất quan",
                "trọng: khi $ lớn,",
                "tích vô hướng ^T$ có giá trị tuyệt đối lớn, đẩy hàm softmax vào",
                "vùng gradient tiệm cận 0.",
                "Việc chia cho $\\sqrt{d_k}$ ổn định quá trình lan truyền ngược.",
                "",
                "## 2. Điểm nghẽn lý thuyết",
                "- Xem phân tích chi tiết tại: [[quadratic-memory-bottleneck]].",
                "",
            ]
        ),
    },
    {
        "slug": "multi-head-attention",
        "title": "Multi-Head Attention",
        "page_type": "method",
        "wikilinks": ["scaled-dot-product-attention", "transformer"],
        "yaml_metadata": {
            "summary": "Chiếu song song Q, K, V qua h không gian con độc lập.",
        },
        "markdown_content": "\n".join(
            [
                "# Multi-Head Attention",
                "",
                "Thay vì thực hiện một phép tính attention đơn lẻ với số chiều {",
                "ext{model}}$,",
                "Multi-Head Attention chiếu , K, V$ qua $ không gian con tuyến",
                "tính độc lập:",
                "",
                "922233  ext{MultiHead}(Q, K, V) =       ext{Concat}(",
                "ext{head}_1, \\ldots,    ext{head}_h)W^O922233",
                "",
                "922233\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)922233",
                "",
                "Giúp mô hình đồng thời nắm bắt quan hệ cú pháp và ngữ nghĩa ở các",
                "vị trí khác nhau",
                "trong kiến trúc [[transformer]].",
                "",
            ]
        ),
    },
    {
        "slug": "lora",
        "title": "LoRA: Low-Rank Adaptation",
        "page_type": "method",
        "wikilinks": ["transformer", "gpt-3", "llama"],
        "yaml_metadata": {
            "authors": ["Edward J. Hu", "Yelong Shen", "Phillip Wallis"],
            "year": 2021,
            "summary": (
                "Kỹ thuật tinh chỉnh tham số hiệu quả (PEFT) bằng phân rã hạng thấp. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# LoRA (Low-Rank Adaptation)",
                "",
                "Kỹ thuật tinh chỉnh tham số hiệu quả (PEFT) đề xuất bởi Hu et al.",
                "(2021) cho [[transformer]].",
                "",
                "## 1. Cơ chế biến đổi ma trận",
                "Đóng băng ma trận trọng số gốc  \\in \\mathbb{R}^{d \times k}$ và phân rã",
                "phần biến thiên cập nhật trọng số $\\Delta W$ thành tích hai ma",
                "trận có hạng thấp $:",
                "",
                "922233W = W_0 + \\Delta W = W_0 + \x0crac{\x07lpha}{r} B \\cdot A922233",
                "",
                "trong đó  \\in \\mathbb{R}^{d \times r}$ khởi tạo bằng 0,",
                " \\in \\mathbb{R}^{r \times k}$ khởi tạo phân phối chuẩn Gaussian.",
                "",
                "## 2. Lợi ích",
                "- Giảm 10,000 lần số tham số cần huấn luyện trên [[gpt-3]] và",
                "[[llama]].",
                "- Không gây thêm bất kỳ độ trễ suy luận nào khi hòa trộn trọng số",
                "vào mô hình gốc.",
                "",
            ]
        ),
    },
    {
        "slug": "react",
        "title": "ReAct: Synergizing Reasoning and Acting",
        "page_type": "method",
        "wikilinks": ["chain-of-thought", "toolformer", "credit-assignment-tool-agents"],
        "yaml_metadata": {
            "authors": ["Shunyu Yao", "Jeffrey Zhao", "Dian Yu", "Nan Du", "Izhak Shafran"],
            "year": 2022,
            "summary": (
                "Mô hình tương tác đan xen giữa suy luận từng bước và gọi công cụ. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# ReAct (Reasoning + Acting)",
                "",
                "Mô hình tương tác đan xen giữa suy luận từng bước ([[chain-of-",
                "thought]]) và hành động",
                "tương tác với môi trường bên ngoài ([[toolformer]]).",
                "",
                "## 1. Vòng lặp ReAct",
                "",
                "922233  ext{Thought}  ightarrow       ext{Action}  ightarrow",
                "ext{Observation}  ightarrow       ext{Thought} \\ldots922233",
                "",
                "- **Thought**: Giúp agent phân tích kế hoạch và xử lý ngoại lệ.",
                "- **Action**: Kích hoạt công cụ truy xuất tri thức, máy tính hoặc",
                "API môi trường.",
                "- **Observation**: Dữ liệu hồi đáp thực tế từ môi trường để điều",
                "chỉnh lập luận.",
                "",
                "## 2. Rào cản mở",
                "- Xem chi tiết tại: [[credit-assignment-tool-agents]].",
                "",
            ]
        ),
    },
    {
        "slug": "retrieval-augmented-generation",
        "title": "Retrieval-Augmented Generation (RAG)",
        "page_type": "method",
        "wikilinks": ["graphrag", "ragas", "llama", "hallucination-in-rag"],
        "yaml_metadata": {
            "authors": ["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus", "Fabio Petroni"],
            "year": 2020,
            "summary": (
                "Kiến trúc kết hợp giữa truy xuất văn bản ngoại sinh và sinh văn bản. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# Retrieval-Augmented Generation (RAG)",
                "",
                "Khung kiến trúc kết hợp giữa mô hình truy xuất thông tin phi tham",
                "số (Dense Vector Index /",
                "[[graphrag]]) và mô hình sinh tham số ([[llama]], [[gpt-3]]) để",
                "giải quyết vấn đề",
                "ảo giác và tri thức lỗi thời.",
                "",
                "## 1. Đánh giá chất lượng",
                "Sử dụng khung đánh giá [[ragas]] đo lường độ trung thực",
                "(Faithfulness) và mức độ",
                "liên quan câu trả lời (Answer Relevance).",
                "",
                "## 2. Điểm nghẽn",
                "- Xem chi tiết tại: [[hallucination-in-rag]].",
                "",
            ]
        ),
    },
    {
        "slug": "graphrag",
        "title": "Graph RAG",
        "page_type": "method",
        "wikilinks": ["retrieval-augmented-generation", "transformer"],
        "yaml_metadata": {
            "summary": (
                "Phương pháp RAG nâng cao kết hợp đồ thị tri thức với phân cụm Leiden. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# Graph RAG (Graph Retrieval-Augmented Generation)",
                "",
                "Phương pháp tiếp cận RAG nâng cao kết hợp đồ thị tri thức với",
                "phân cụm đồ thị",
                "(Leiden Community Detection) để trả lời các câu hỏi tóm tắt toàn cục.",
                "",
                "## 1. So sánh với RAG truyền thống",
                "- **Vector RAG**: Tìm kiếm điểm tương đồng cục bộ giữa vector",
                "truy vấn và văn bản.",
                "- **Graph RAG**: Tổng hợp tri thức xuyên suốt toàn bộ tập tài",
                "liệu thông qua đồ thị.",
                "",
            ]
        ),
    },
    {
        "slug": "chain-of-thought",
        "title": "Chain-of-Thought (CoT) Prompting",
        "page_type": "method",
        "wikilinks": ["gpt-3", "react"],
        "yaml_metadata": {
            "authors": ["Jason Wei", "Xuezhi Wang", "Dale Schuurmans"],
            "year": 2022,
            "summary": (
                "Kỹ thuật khơi gợi chuỗi suy luận trung gian trước khi đưa ra câu trả lời. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# Chain-of-Thought (CoT) Prompting",
                "",
                "Kỹ thuật khơi gợi chuỗi suy luận logic trung gian trước khi đưa",
                "ra câu trả lời cuối cùng",
                "trên các mô hình ngôn ngữ lớn như [[gpt-3]] và [[llama]].",
                "",
                "Phát triển nền tảng cho các hệ thống Agent tự trị như [[react]].",
                "",
            ]
        ),
    },
    {
        "slug": "direct-preference-optimization",
        "title": "Direct Preference Optimization (DPO)",
        "page_type": "method",
        "wikilinks": ["llama", "gpt-3"],
        "yaml_metadata": {
            "authors": ["Rafael Rafailov", "Archit Sharma", "Eric Mitchell"],
            "year": 2023,
            "summary": (
                "Căn chỉnh mô hình ngôn ngữ theo sở thích con người bằng hàm tối ưu đóng. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# Direct Preference Optimization (DPO)",
                "",
                "Phương pháp căn chỉnh mô hình ngôn ngữ theo sở thích con người mà",
                "không cần huấn luyện",
                "mô hình phần thưởng độc lập (Reward Model) hay lấy mẫu phức tạp",
                "như RLHF PPO.",
                "",
                "## 1. Hàm mục tiêu tối ưu",
                "",
                "922233\\mathcal{L}_{     ext{DPO}}(\\pi_  heta; \\pi_{",
                "ext{ref}}) = -\\mathbb{E}_{(x, y_w, y_l)} \\left[ \\log \\sigma",
                "\\left( \x08eta \\log  rac{\\pi_  heta(y_w|x)}{\\pi_{",
                "ext{ref}}(y_w|x)} - \x08eta \\log  rac{\\pi_ heta(y_l|x)}{\\pi_{",
                "ext{ref}}(y_l|x)}  ight)  ight]922233",
                "",
            ]
        ),
    },
    {
        "slug": "bert",
        "title": "BERT: Bidirectional Transformers",
        "page_type": "topic",
        "wikilinks": ["transformer", "attention-is-all-you-need"],
        "yaml_metadata": {
            "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
            "year": 2018,
            "summary": (
                "Mô hình tiền huấn luyện ngôn ngữ hai chiều sâu dựa trên Transformer Encoder. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# BERT (Bidirectional Encoder Representations from Transformers)",
                "",
                "Mô hình tiền huấn luyện hai chiều dựa trên [[transformer]] với",
                "mục tiêu Masked Language",
                "Model (MLM) và Next Sentence Prediction (NSP).",
                "",
            ]
        ),
    },
    {
        "slug": "llama",
        "title": "LLaMA Foundation Models",
        "page_type": "topic",
        "wikilinks": ["transformer", "lora", "direct-preference-optimization"],
        "yaml_metadata": {
            "authors": ["Hugo Touvron", "Thibaut Lavril", "Gautier Izacard"],
            "year": 2023,
            "summary": (
                "Bộ sưu tập các mô hình ngôn ngữ nền tảng mã nguồn mở hiệu năng cao. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# LLaMA Foundation Models",
                "",
                "Dòng mô hình ngôn ngữ nền tảng mã nguồn mở hiệu năng cao huấn",
                "luyện hoàn toàn trên dữ liệu",
                "công khai, làm nền tảng cho tinh chỉnh với [[lora]] và căn chỉnh với",
                "[[direct-preference-optimization]].",
                "",
            ]
        ),
    },
    {
        "slug": "quadratic-memory-bottleneck",
        "title": "Độ phức tạp tính toán bậc hai O(N^2) trong Self-Attention",
        "page_type": "research_gap",
        "wikilinks": ["scaled-dot-product-attention", "transformer", "attention-is-all-you-need"],
        "yaml_metadata": {
            "domain": "Efficiency & Long-Context Scalability",
            "bottleneck": (
                "Độ phức tạp tính toán và bộ nhớ O(N^2) của ma trận tích vô hướng "
                "QK^T khi tăng kích thước ngữ cảnh. "
            ).strip(),
            "acknowledged_by": ["Vaswani et al. (2017)", "Touvron et al. (2023)"],
            "potential_solution": (
                "FlashAttention-2 với tối ưu hóa phần cứng SRAM, hoặc State Space Models (Mamba). "
            ).strip(),
            "summary": (
                "Rào cản tính toán cốt tử khi mở rộng chiều dài chuỗi token trong Attention. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# Điểm nghẽn độ phức tạp bậc hai O(N^2) trong Self-Attention",
                "",
                "Cơ chế [[scaled-dot-product-attention]] trong [[transformer]] có",
                "độ phức tạp tính toán",
                "và bộ nhớ tỷ lệ với bình phương độ dài chuỗi (N^2)$, gây cản trở",
                "nghiêm trọng",
                "khi mở rộng ngữ cảnh văn bản lên hàng triệu token.",
                "",
                "## 1. Tài liệu ghi nhận",
                "- [[attention-is-all-you-need]] (Vaswani et al., 2017)",
                "- [[llama]] (Touvron et al., 2023)",
                "",
                "## 2. Hướng nghiên cứu tiềm năng",
                "- Cấu trúc không gian trạng thái tuyến tính (State Space Models /",
                "Mamba)",
                "- Kỹ thuật tính toán tối ưu hóa bộ nhớ đệm SRAM (FlashAttention-2/3)",
                "- Cơ chế chú ý thưa (Sparse & Sliding Window Attention)",
                "",
            ]
        ),
    },
    {
        "slug": "hallucination-in-rag",
        "title": "Xung đột tri thức và hiện tượng ảo giác trong RAG",
        "page_type": "research_gap",
        "wikilinks": ["retrieval-augmented-generation", "graphrag", "ragas"],
        "yaml_metadata": {
            "domain": "Robustness & Trustworthiness",
            "bottleneck": (
                "Mâu thuẫn ngữ nghĩa giữa tri thức tiền huấn luyện trong trọng số "
                "tham số và ngữ cảnh ngoại sinh dẫn tới hiện tượng hallucination. "
            ).strip(),
            "acknowledged_by": ["Lewis et al. (2020)", "Es et al. (2023)"],
            "potential_solution": (
                "GraphRAG kết hợp kiểm chứng đa chặng và chỉ số RAGAS Faithfulness. "
            ).strip(),
            "summary": (
                "Hiện tượng mô hình tạo lập thông tin sai lệch khi đối chiếu tài liệu. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# Xung đột tri thức và hiện tượng ảo giác trong Retrieval-",
                "Augmented Generation",
                "",
                "Dù [[retrieval-augmented-generation|RAG]] giúp bổ sung tri thức",
                "ngoại sinh, mô hình vẫn",
                "thường xuyên gặp hiện tượng ảo giác (hallucination) khi ngữ cảnh",
                "truy xuất chứa",
                "thông tin mâu thuẫn hoặc không đầy đủ.",
                "",
                "## 1. Tài liệu ghi nhận",
                "- Lewis et al. (2020) - [[retrieval-augmented-generation]]",
                "- Es et al. (2023) - [[ragas]]",
                "",
                "## 2. Hướng giải quyết",
                "- Ứng dụng [[graphrag]] để kiểm chứng chéo quan hệ thực thể.",
                "- Tự động đánh giá độ trung thực (Faithfulness) với [[ragas]].",
                "",
            ]
        ),
    },
    {
        "slug": "credit-assignment-tool-agents",
        "title": "Phân bổ trách nhiệm lỗi trong Agent tự trị đa chặng",
        "page_type": "research_gap",
        "wikilinks": ["react", "toolformer", "chain-of-thought"],
        "yaml_metadata": {
            "domain": "Agentic Reasoning & Multi-Step Planning",
            "bottleneck": (
                "Sai lệch tích lũy qua chuỗi gọi công cụ liên tiếp mà không có khả "
                "năng tự quay lui (backtracking) để phục hồi trạng thái đúng. "
            ).strip(),
            "acknowledged_by": ["Yao et al. (2022)", "Schick et al. (2023)"],
            "potential_solution": (
                "Lập kế hoạch dạng cây (Tree of Thoughts) kết hợp vòng tự đánh giá (Critic Loop). "
            ).strip(),
            "summary": (
                "Thách thức phân bổ lỗi khi Agent thực hiện chuỗi quyết định phức tạp. "
            ).strip(),
        },
        "markdown_content": "\n".join(
            [
                "# Rào cản phân bổ trách nhiệm (Credit Assignment) trong ReAct và",
                "Toolformer",
                "",
                "Khi Agent thực hiện chuỗi hành động đa bước qua [[react]] hoặc",
                "gọi công cụ qua",
                "[[toolformer]], một lỗi sai ở bước trung gian sẽ lan truyền dây",
                "chuyền sang các bước",
                "tiếp theo mà mô hình không thể tự nhận thức và quay lui",
                "(backtracking).",
                "",
                "## 1. Tài liệu ghi nhận",
                "- Yao et al. (2022) - [[react]]",
                "- Schick et al. (2023) - [[toolformer]]",
                "",
                "## 2. Hướng giải quyết",
                "- Tích hợp tìm kiếm cây học thuật (Tree of Thoughts / Monte Carlo",
                "Tree Search).",
                "- Cơ chế phản hồi tự phê bình (Self-Refine & Critic Loops).",
                "",
            ]
        ),
    },
]
