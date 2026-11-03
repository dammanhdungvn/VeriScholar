from pathlib import Path


def test_fig3_2_coordinates_within_safe_margins():
    tex_path = Path("report-datn/chapters/ch3/3_3_kien_truc.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra scale đã giảm về <= 0.68 (0.65 để an toàn tuyệt đối cách lề >= 5mm)
    assert "scale=0.65" in content or "scale=0.68" in content, (
        "Hình 3-2 phải sử dụng scale <= 0.68 để vừa vặn lề in textwidth=16cm"
    )

    # Kiểm tra tọa độ Adapter không vượt quá +- 8.8 (trước đây là 10.4)
    assert "(10.4," not in content, (
        "Tọa độ x của Driven Adapter vẫn còn 10.4 gây tràn lề phải!"
    )
    assert "(-10.4," not in content, (
        "Tọa độ x của Driving Adapter vẫn còn -10.4!"
    )
    assert "(8.8," in content or "(8.80," in content, (
        "Thiếu tọa độ x=8.8 cho Driven Adapter"
    )
    assert "(-8.8," in content or "(-8.80," in content, (
        "Thiếu tọa độ x=-8.8 cho Driving Adapter"
    )


def test_fig2_4_loop_and_label_styling():
    tex_path = Path("report-datn/chapters/ch2/2_5_agentic_react.tex")
    content = tex_path.read_text(encoding="utf-8")

    # Kiểm tra cung tròn vòng lặp đỏ không vồng quá cao
    assert "to[out=110, in=250]" in content or "to[out=115, in=245]" in content, (
        "Cung lặp đỏ cần dùng out=110, in=250 để không vượt quá đỉnh hộp agent"
    )

    # Kiểm tra nhãn rẽ nhánh có padding và fill=white
    assert "inner sep=2pt" in content, (
        "Nhãn rẽ nhánh hình thoi cần inner sep=2pt để không dính nét vẽ hình thoi"
    )

    # Kiểm tra có đệm vspace trước caption
    assert "\\vspace{4pt}" in content or "\\vspace{6pt}" in content, (
        "Cần vspace trước caption để tránh đáy hộp PDF dính sát caption"
    )

