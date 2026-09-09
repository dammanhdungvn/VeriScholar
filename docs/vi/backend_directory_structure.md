## Cấu trúc thư mục backend

```text
src/apps/api/src/api/
├── core/                           # Cấu hình lõi & Base classes
│   ├── config.py                   # Quản lý biến môi trường, API keys (Pydantic Settings)
│   ├── state.py                    # Schema ResearchState (LangGraph Shared State & Reducers)
│   └── schemas.py                  # DTOs: DocumentChunk, Claim, ComparisonMatrix
│
├── parsers/                        # Tầng xử lý & bóc tách dữ liệu thô
│   ├── base.py                     # Abstract Base Parser
│   ├── layout_parser.py            # Geometry-aware PDF Parser (2 cột, reading order, bounding box)
│   └── table_extractor.py          # Trích xuất bảng biểu sang Markdown & Math equations
│
├── storage/                        # Tầng lưu trữ độc lập (3 topologies)
│   ├── file_store.py               # Quản lý file PDF thô & assets
│   ├── vector_store.py             # Hybrid Vector Index (Dense + BM25)
│   └── state_store.py              # Checkpointer lưu State phiên làm việc & Scratchpad
│
├── subagents/                      # Các Subagent chuyên trách (Specialist Subagents)
│   ├── supervisor.py               # Supervisor Agent (Phân loại intent & điều phối graph)
│   ├── reader/                     # Module 1: Single Paper Deep Read
│   │   ├── agent.py                # Analytical Reader Subagent
│   │   ├── tools.py                # Tools: trỏ trang gốc, trích 3 ý chính, note vào scratchpad
│   │   └── prompts.py
│   ├── writer/                     # Module 2: Literature Review & Verification
│   │   ├── agent.py                # Synthesis/Writer Subagent
│   │   ├── fact_checker.py         # Batched Claim Verification Pipeline (NLI)
│   │   └── compiler.py             # ReAct Compiler Agent giao tiếp E2B Sandbox
│   ├── discovery/                  # Module 3: External Paper Discovery & Roadmap
│   │   ├── agent.py
│   │   └── search_tools.py         # Cổng API ArXiv, Semantic Scholar, Crossref
│   └── library/                    # Module 4: Multi-paper Library & Matrix
│       ├── agent.py
│       └── matrix_builder.py       # Map-Reduce so sánh đa bài báo
│
├── sandboxes/                      # Hạ tầng thực thi cách ly E2B
│   ├── latex_sandbox.py            # Kết nối & quản lý vòng đời Custom E2B LaTeX Sandbox
│   └── error_parser.py             # Parser lọc mã lỗi STDERR từ pdflatex / latexmk
│
├── eval_rag/                       # Bộ kiểm định chất lượng (Evaluation & Observability)
│   ├── metrics.py                  # RAG Triad (Faithfulness, Relevance, Context Precision)
│   └── golden_dataset.py           # Bộ 50 benchmark Q&A học thuật chuẩn
│
└── main.py                         # Điểm khởi chạy ứng dụng / Graph Entrypoint
```
