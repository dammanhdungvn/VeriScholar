import type { IdeaPrompt, SessionItem, ChatMessage } from "@/types/dashboard";

export const IDEAS_FOR_YOU: IdeaPrompt[] = [
  {
    id: "idea-1",
    title: "Tóm tắt 3 luận điểm cốt lõi",
    subtitle: "Trích xuất 3 luận điểm then chốt kèm số trang",
    prompt: "Tóm tắt 3 luận điểm khoa học cốt lõi của bài báo này kèm số trang và tọa độ bằng chứng.",
    iconName: "FileText"
  },
  {
    id: "idea-2",
    title: "Thẩm định tiền đề giả thuyết",
    subtitle: "Rà soát phản biện logic và phát hiện ngộ nhận",
    prompt: "Kiểm tra xem câu hỏi sau có chứa tiền đề sai lệch với thực tế bài báo không: 'Cơ chế RNN được đặt ở tầng encoder thứ mấy?'",
    iconName: "ShieldAlert"
  },
  {
    id: "idea-3",
    title: "Đúc kết tri thức sang Sổ tay",
    subtitle: "Biên soạn digest học thuật chuẩn IEEE/APA",
    prompt: "Tổng hợp các ghi chú đã đánh dấu thành một bản đúc kết tri thức có cấu trúc logic.",
    iconName: "BookOpen"
  }
];

export const RECENT_SESSIONS: SessionItem[] = [
  {
    id: "session-vaswani-2017",
    title: "Attention Is All You Need (Vaswani et al.)",
    document_ids: ["doc-vaswani-2017"],
    created_at: "2026-09-18T10:00:00.000Z",
    updated_at: "2026-09-19T14:00:00.000Z",
    version: 1,
    unread: false
  },
  {
    id: "session-he-2016",
    title: "Deep Residual Learning for Image Recognition",
    document_ids: ["doc-he-2016"],
    created_at: "2026-09-17T09:30:00.000Z",
    updated_at: "2026-09-18T16:20:00.000Z",
    version: 1,
    unread: false
  },
  {
    id: "session-lewis-2020",
    title: "Retrieval-Augmented Generation for Knowledge Tasks",
    document_ids: ["doc-lewis-2020"],
    created_at: "2026-09-16T14:15:00.000Z",
    updated_at: "2026-09-17T11:45:00.000Z",
    version: 1,
    unread: false
  }
];

export const SAMPLE_CHAT_MESSAGES: Record<string, ChatMessage[]> = {
  "session-vaswani-2017": [
    {
      id: "msg-1",
      session_id: "session-vaswani-2017",
      role: "user",
      content: "Giải thích cơ chế Multi-Head Attention và công thức tính Scaled Dot-Product Attention trong bài báo?",
      created_at: "2026-09-19T14:02:00.000Z"
    },
    {
      id: "msg-2",
      session_id: "session-vaswani-2017",
      role: "assistant",
      content: `Cơ chế **Scaled Dot-Product Attention** là nền tảng cốt lõi của Transformer, tính toán mức độ tập trung trọng số giữa các vector Queries ($Q$), Keys ($K$), và Values ($V$):

$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$

Trong đó đại lượng phân số $\\frac{1}{\\sqrt{d_k}}$ đóng vai trò chuẩn hóa kích thước, ngăn chặn tích vô hướng tăng quá lớn ở các không gian chiều cao làm trôi gradient về vùng bão hòa của hàm softmax.

Thay vì tính toán attention một lần duy nhất với số chiều $d_{\\text{model}}$, bài báo chiếu tuyến tính $Q, K, V$ sang $h = 8$ không gian con khác nhau (**Multi-Head Attention**):

$$\\text{MultiHead}(Q, K, V) = \\text{Concat}(\\text{head}_1, \\dots, \\text{head}_h)W^O$$

Điều này cho phép mô hình đồng thời chú ý đến thông tin từ các không gian biểu diễn khác nhau ở các vị trí khác nhau.`,
      created_at: "2026-09-19T14:02:05.000Z",
      citations: [
        {
          paper_id: "doc-vaswani-2017",
          paper_title: "Attention Is All You Need",
          page: 4,
          bbox: [0.12, 0.28, 0.48, 0.42, 4]
        },
        {
          paper_id: "doc-vaswani-2017",
          paper_title: "Attention Is All You Need",
          page: 5,
          bbox: [0.52, 0.15, 0.88, 0.35, 5]
        }
      ]
    },
    {
      id: "msg-3",
      session_id: "session-vaswani-2017",
      role: "user",
      content: "Tác giả đặt cơ chế RNN ở tầng encoder thứ mấy để giữ thứ tự từ?",
      created_at: "2026-09-19T14:05:00.000Z"
    },
    {
      id: "msg-4",
      session_id: "session-vaswani-2017",
      role: "assistant",
      content: `Câu hỏi của bạn chứa một tiền đề không chính xác so với cấu trúc thực tế của bài báo.

Kiến trúc Transformer **hoàn toàn không sử dụng RNN hay bất kỳ mạng đệ quy nào** ở bất cứ tầng nào. Thay vào đó, để nắm bắt thứ tự của các từ trong chuỗi, các tác giả đã đề xuất phương pháp **Positional Encoding** (Mã hóa Vị trí) sử dụng các hàm lượng giác sin và cosin với tần số khác nhau:

$$PE_{(pos, 2i)} = \\sin\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$
$$PE_{(pos, 2i+1)} = \\cos\\left(\\frac{pos}{10000^{2i/d_{\\text{model}}}}\\right)$$

Vector mã hóa vị trí này được cộng trực tiếp vào vector nhúng từ (input embeddings) trước khi đưa vào khối Encoder đầu tiên.`,
      created_at: "2026-09-19T14:05:06.000Z",
      presupposition_alert: {
        flawed_premise: "Tác giả sử dụng mạng RNN trong Encoder để lưu thứ tự từ",
        correction: "Transformer loại bỏ hoàn toàn RNN; sử dụng Positional Encoding lượng giác",
        grounded_bbox: [0.15, 0.62, 0.85, 0.88, 6],
        page: 6
      },
      citations: [
        {
          paper_id: "doc-vaswani-2017",
          paper_title: "Attention Is All You Need",
          page: 6,
          bbox: [0.15, 0.62, 0.85, 0.88, 6]
        }
      ]
    }
  ]
};
