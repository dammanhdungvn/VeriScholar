# VeriScholar Offline NLI Models

This directory contains offline checkpoints for dedicated Natural Language Inference (NLI) classification used by the SAFE (Search-Augmented Factuality Evaluator) engine according to PRD §3.2.

---

## 1. Primary Model: `cross-encoder/nli-deberta-v3-small`

- **Repository:** [`cross-encoder/nli-deberta-v3-small`](https://huggingface.co/cross-encoder/nli-deberta-v3-small)
- **Base Architecture:** `microsoft/deberta-v3-small` (`DebertaV2ForSequenceClassification`)
- **Revision / Commit SHA:** `fa2804872c3b4bd748f38c0185cc85775361e735`
- **License:** Apache-2.0
- **Training Datasets:** MultiNLI (`nyu-mll/multi_nli`) + SNLI (`stanfordnlp/snli`)
- **Supported Language:** English (`en`)
- **3-Way Label Mapping (`id2label`):**
  - Index `0`: `contradiction` $\rightarrow$ VeriScholar `contradicted`
  - Index `1`: `entailment` $\rightarrow$ VeriScholar `supported`
  - Index `2`: `neutral` $\rightarrow$ VeriScholar `not_enough_info`

### Artifacts in `cross-encoder-nli-deberta-v3-small/`:
- `config.json`: Model configuration and `id2label` definitions (1,052 bytes)
- `tokenizer.json`: Fast Rust-based HuggingFace tokenizer (8,656,624 bytes)
- `tokenizer_config.json`: Tokenizer special tokens and padding rules (1,346 bytes)
- `special_tokens_map.json`: `[CLS]`, `[SEP]`, `[PAD]`, `[UNK]`, `[MASK]` (301 bytes)
- `spm.model`: SentencePiece vocabulary binary (2,464,616 bytes)
- `onnx/model_quint8_avx2.onnx`: INT8 AVX2 quantized neural network weights (172,503,005 bytes / 164.51 MB)

### Empirical Benchmarks (Measured on Linux Host, 8 vCPUs):
- **Bundle Size on Disk:** 183.6 MB (175.12 MiB)
- **Model Load Time:** 776.02 ms
- **Peak Process Memory:** 534.57 MB (within PRD §3.2 memory envelope)
- **Inference Latency (50 runs on CPU):**
  - **p50:** 12.71 ms
  - **p95:** 21.41 ms
  - **Mean:** 13.93 ms
  - **Min:** 9.64 ms
  - **Max:** 23.42 ms

---

## 2. Multilingual / Vietnamese Policy (PRD & Technical Directive)

- As specified by coordinator directives, `cross-encoder/nli-deberta-v3-small` is formally verified only for **English scientific literature**.
- For non-English / Vietnamese claims, the system applies an explicit fallback strategy to lexical/numerical evidence matching or signals unverified language rather than fabricating ungrounded neural verdicts.
