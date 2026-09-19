import type { DemoPaper } from "@/types/landing";

export const MOCK_DEMO_PAPERS: DemoPaper[] = [
  {
    id: "demo-paper-attention",
    title: "Attention Is All You Need",
    authors: "Ashish Vaswani, Noam Shazeer, Niki Parmar, et al.",
    venue_year: "NeurIPS 2017",
    total_pages: 15,
    page_dimensions: { width_pt: 595.28, height_pt: 841.89 },
    rotation_deg: 0,
    sample_turns: [
      {
        id: "turn-1",
        user_query: "Tác giả đặt cơ chế RNN ở tầng encoder thứ mấy để duy trì thông tin vị trí từ?",
        ai_thought:
          "Thẩm định tiền đề câu hỏi (Presupposition Validation): Người dùng giả định mô hình Transformer sử dụng RNN trong encoder để mã hóa thứ tự từ. Tuy nhiên, theo Mục 3.5 (Trang 6), Transformer loại bỏ hoàn toàn đệ quy RNN và tích chập CNN, thay bằng Positional Encoding dùng hàm Sin/Cos.",
        presupposition_corrected: true,
        ai_answer_markdown:
          "**Phát hiện sai lệch tiền đề:** Kiến trúc Transformer trong bài báo **không sử dụng bất kỳ tầng RNN nào**. Thay vào đó, để mô hình nhận biết được thứ tự các từ trong câu mà không cần cơ chế đệ quy tuần tự, nhóm tác giả đề xuất kỹ thuật **Positional Encoding** (Mã hóa Vị trí) dựa trên hàm Sin và Cosin ở các tần số khác nhau được cộng trực tiếp vào vector nhúng đầu vào:\n\n$$\\text{PE}_{(\\text{pos}, 2i)} = \\sin\\left(\\frac{\\text{pos}}{10000^{2i/d_{\\text{model}}}}\\right)$$\n\n$$\\text{PE}_{(\\text{pos}, 2i+1)} = \\cos\\left(\\frac{\\text{pos}}{10000^{2i/d_{\\text{model}}}}\\right)$$",
        citations: [
          {
            id: "cite-pos-enc",
            label: "Attention Is All You Need • Mục 3.5 (Tr. 6)",
            paper_title: "Attention Is All You Need",
            page: 6,
            bounding_box: [0.08, 0.42, 0.48, 0.58, 6],
            quote_text:
              "Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute positions of the tokens in the sequence. To this end, we add 'positional encodings' to the input embeddings...",
            fact_check_status: "supported",
          },
        ],
      },
      {
        id: "turn-2",
        user_query: "Công thức toán học của Scaled Dot-Product Attention được định nghĩa thế nào?",
        ai_thought:
          "Truy xuất định nghĩa toán học Scaled Dot-Product Attention từ Mục 3.2.1 (Trang 4), công thức (1). Hệ số căn bậc hai của d_k đóng vai trò điều hòa gradient ở vùng bão hòa softmax.",
        presupposition_corrected: false,
        ai_answer_markdown:
          "Theo Mục 3.2.1 (Trang 4), **Scaled Dot-Product Attention** được tính bằng tích vô hướng giữa ma trận Query ($Q$) và Key ($K$), chia cho hệ số co giãn $\\sqrt{d_k}$ để ngăn chặn hiện tượng gradient bị triệt tiêu khi tích vô hướng quá lớn, sau đó chuẩn hóa qua hàm Softmax và nhân với ma trận Value ($V$):\n\n$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$\n\nCơ chế này cho phép tính toán song song hoàn toàn ma trận trọng số trên phần cứng hiện đại.",
        citations: [
          {
            id: "cite-attention-formula",
            label: "Attention Is All You Need • Mục 3.2.1 (Tr. 4)",
            paper_title: "Attention Is All You Need",
            page: 4,
            bounding_box: [0.52, 0.22, 0.92, 0.36, 4],
            quote_text:
              "We compute the attention function on a set of queries simultaneously, packed together into a matrix Q. The keys and values are also packed into matrices K and V. We compute the matrix of outputs as: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
            fact_check_status: "supported",
          },
        ],
      },
    ],
    mock_page_paragraphs: [
      {
        column: 1,
        text: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks in an encoder-decoder configuration. The best performing models also connect the encoder and decoder through an attention mechanism.",
      },
      {
        column: 1,
        text: "We propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality.",
      },
      {
        column: 1,
        text: "3.5 Positional Encoding: Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute positions of the tokens in the sequence. To this end, we add 'positional encodings' to the input embeddings at the bottoms of the encoder and decoder stacks.",
        has_formula: true,
        formula_text: "\\text{PE}_{(\\text{pos}, 2i)} = \\sin(\\text{pos} / 10000^{2i/d_{\\text{model}}})",
      },
      {
        column: 2,
        text: "3.2.1 Scaled Dot-Product Attention: We call our particular attention 'Scaled Dot-Product Attention'. The input consists of queries and keys of dimension d_k, and values of dimension d_v. We compute the dot products of the query with all keys, divide each by sqrt(d_k), and apply a softmax function.",
        has_formula: true,
        formula_text: "\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
      },
      {
        column: 2,
        text: "Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this capability.",
      },
    ],
  },
  {
    id: "demo-paper-resnet",
    title: "Deep Residual Learning for Image Recognition",
    authors: "Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun",
    venue_year: "CVPR 2016 (Best Paper)",
    total_pages: 12,
    page_dimensions: { width_pt: 595.28, height_pt: 841.89 },
    rotation_deg: 0,
    sample_turns: [
      {
        id: "turn-resnet-1",
        user_query: "Mạng ResNet giải quyết hiện tượng suy thoái (degradation problem) bằng cơ chế cốt lõi nào?",
        ai_thought:
          "Truy xuất khái niệm Residual Mapping và Identity Shortcut Connection từ Mục 3 (Trang 2). Thay vì fit trực tiếp H(x), mạng fit ánh xạ phần dư F(x) = H(x) - x.",
        presupposition_corrected: false,
        ai_answer_markdown:
          "Khi tăng số tầng mạng lên quá sâu, độ chính xác bị bão hòa và tụt giảm (degradation problem). Thay vì ép các lớp xếp chồng học trực tiếp ánh xạ mục tiêu ban đầu $\\mathcal{H}(x)$, ResNet tái cấu trúc để mạng học **ánh xạ phần dư (Residual Mapping)**:\n\n$$\\mathcal{F}(x) \\coloneqq \\mathcal{H}(x) - x \\implies \\mathcal{H}(x) = \\mathcal{F}(x) + x$$\n\nCơ chế này được thực thi thông qua **đường tắt đồng nhất (Identity Shortcut Connections)** không làm tăng tham số hay độ phức tạp tính toán.",
        citations: [
          {
            id: "cite-resnet-shortcut",
            label: "He et al. • Trang 2",
            paper_title: "Deep Residual Learning for Image Recognition",
            page: 2,
            bounding_box: [0.08, 0.35, 0.48, 0.52, 2],
            quote_text:
              "Instead of hoping each few stacked layers directly fit a desired underlying mapping, we explicitly let these layers fit a residual mapping. Formally, denoting the desired underlying mapping as H(x), we let the stacked nonlinear layers fit another mapping of F(x) := H(x) - x.",
            fact_check_status: "supported",
          },
        ],
      },
    ],
    mock_page_paragraphs: [
      {
        column: 1,
        text: "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions.",
      },
      {
        column: 1,
        text: "3. Deep Residual Learning: When deeper networks are able to start converging, a degradation problem has been exposed: with the network depth increasing, accuracy gets saturated and then degrades rapidly.",
        has_formula: true,
        formula_text: "F(x) := H(x) - x -> H(x) = F(x) + x",
      },
      {
        column: 2,
        text: "The formulation of F(x) + x by shortcut connections neither introduces extra parameter nor computation complexity. The entire network can still be trained end-to-end by SGD with backpropagation.",
      },
      {
        column: 2,
        text: "On the ImageNet dataset, we evaluate our residual nets with a depth of up to 152 layers—8x deeper than VGG nets but still having lower complexity. An ensemble of these residual nets achieves 3.57% top-5 error rate on the ImageNet test set.",
      },
    ],
  },
];
