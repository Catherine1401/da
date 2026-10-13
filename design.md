# Thiết kế chi tiết: danh mục biểu đồ và quy ước dùng chung

Đi kèm `plan.md`. Mỗi biểu đồ có một mã (ví dụ `f2_1`); ảnh xuất ra `out/figs/<mã>.png`, bảng số xuất ra `out/tables/<mã>.csv`.
Mọi con số ở mục 1 là số đo thử một lần trên `data/results.csv`; khi code phải chạy lại trong notebook và dùng số của notebook.

## 1. Kiểm tra khả thi (đã đo)

| Nội dung | Kết quả đo | Quyết định thiết kế |
|---|---|---|
| Bảng lương `df_sal` | 19.576 dòng | Khớp quy tắc lọc mục 4 của `plan.md` |
| 12 vai trò `DevType` đủ ≥200 dòng (đã bỏ "Other") | Từ full-stack 7.075 đến data scientist 219 | Ridgeline dùng 12 nhóm; spider chọn 3 nhóm |
| Số người dùng AI hằng ngày theo vai trò | Từ 29,5% (embedded) đến 73,6% (AI/ML engineer) | Đủ khác biệt để làm trục spider |
| `JobSat` theo vai trò | Mọi vai trò ≥207 dòng có trả lời | Dùng làm trục spider |
| Network ngôn ngữ (42 nút) | 861 cặp đồng xuất hiện; 97 cặp ≥5% người trả lời; 56 cặp ≥10% | Ngưỡng cạnh 10% (56 cạnh) để tránh hairball |
| Sankey "đang dùng → muốn dùng" | 1.764 luồng; 238 luồng ≥1.000 người | Quá nhiều: chỉ vẽ top 8 ngôn ngữ ở mỗi bên |
| Scatter dùng so với ngưỡng mộ | 42 ngôn ngữ, ít nhất 145 người dùng, tỷ lệ ngưỡng mộ 24%–72% | Vẽ đủ 42 điểm, ghi nhãn nhóm nổi bật |
| Heatmap lương 10 ngôn ngữ × 6 vai trò | Ô nhỏ nhất 47 dòng, 0/60 ô dưới 30 | Vẽ được, ô <30 dòng sẽ tô riêng |
| Hồi quy `log(lương)` (17.426 dòng, nước ≥30 dòng, 15 ngôn ngữ phổ biến nhất) | R² chỉ quốc gia 0,450; thêm kinh nghiệm 0,523; thêm 15 ngôn ngữ 0,548; chỉ kinh nghiệm + ngôn ngữ (không quốc gia) 0,235 | Sơ bộ ủng hộ giả thuyết "quốc gia và kinh nghiệm quan trọng hơn ngôn ngữ"; chưa kết luận, phải chạy lại trong notebook và kiểm tra thêm |

Hạn chế của số đo hồi quy: chỉ 15 ngôn ngữ phổ biến nhất, chưa kiểm tra đa cộng tuyến, mô hình mô tả không chứng minh nhân quả.

## 2. Quy ước dùng chung (khai báo ở ô cấu hình, mọi người dùng lại)

| Mục | Quy ước |
|---|---|
| Kích thước ảnh | 1600 × 900 px (16:9), 200 dpi, nền trắng; một ảnh dùng cho cả slide và báo cáo |
| Font | Mặc định DejaVu Sans của matplotlib; không đổi font |
| Màu | Bảng Okabe-Ito (an toàn cho người mù màu): màu nhấn chính xanh `#0072B2`, màu nhấn phụ cam đỏ `#D55E00`, trung tính xám `#999999`. Việt Nam luôn dùng màu nhấn phụ |
| Mã hóa không chỉ bằng màu | Thêm nhãn trực tiếp hoặc ký hiệu |
| Tiêu đề | Cấp 2 hoặc 3 (nêu phát hiện), viết sau khi thấy số liệu; mẫu nháp ở mục 3 chỉ là giả thuyết |
| Chú thích chân biểu đồ | Một dòng: nguồn, bộ lọc, `n`, đơn vị (ví dụ "Nguồn: Stack Overflow Developer Survey 2025; lập trình viên chuyên nghiệp, lương 1.000–500.000 USD; n = 19.576; USD danh nghĩa") |
| Số | Dấu chấm phân tách hàng nghìn, dấu phẩy thập phân (cùng kiểu với báo cáo) |
| Lương | Median kèm khoảng tin cậy 95% bootstrap khi nhóm có <1.000 dòng |
| Nhận xét | Mỗi biểu đồ kèm 3–5 câu "Nhận xét" và 1–2 câu "Insight" lưu ở `out/tables/<mã>_note.txt` để docx và slide dùng lại |

## 3. Danh mục biểu đồ

Cột "Dữ liệu": `all` là `df_all` (49.191 dòng, mẫu số là số người có trả lời cột đó), `sal` là `df_sal` (19.576 dòng). Người làm theo mục 10 của `plan.md`.

| Mã | Câu hỏi | Người | Dữ liệu | Biểu đồ và thư viện | Nội dung | Tiêu đề nháp (giả thuyết) |
|---|---|---|---|---|---|---|
| f1_1 | Q1 | B | all | Bar ngang, matplotlib | `MainBranch` | Phần lớn người trả lời là lập trình viên chuyên nghiệp |
| f1_2 | Q1 | B | all | Bar, matplotlib | `Age` theo nhóm tuổi | Người trả lời tập trung ở nhóm 25–34 tuổi |
| f1_3 | Q1 | B | all | Bar ngang top 15, matplotlib | `Country` (số phản hồi), Việt Nam tô màu nhấn phụ | Mẫu lệch về Mỹ, Đức, Ấn Độ; Việt Nam chỉ 145 phản hồi |
| f2_1 | Q2 | B | all | Bar ngang top 15 | `LanguageHaveWorkedWith`, % người trả lời | Một vài ngôn ngữ chiếm phần lớn mức sử dụng |
| f2_2 | Q2 | B | all | Treemap, `px.treemap` | Nhóm (ngôn ngữ, CSDL, cloud, web framework) → công nghệ top 8, diện tích theo số người dùng | Bức tranh hệ sinh thái theo nhóm |
| f2_3 | Q2 | B | all | Bar nhỏ lặp (small multiples) | Top CSDL, cloud, web framework | Công nghệ nổi bật theo từng nhóm |
| f3_1 | Q3 | B | all | Scatter, matplotlib | Trục x: % đang dùng, trục y: % ngưỡng mộ (`Admired / HaveWorkedWith`), 42 ngôn ngữ | Dùng nhiều chưa chắc được ngưỡng mộ nhiều |
| f3_2 | Q3 | B | all | Bar phân kỳ | Chênh lệch `WantToWorkWith` trừ `HaveWorkedWith` (điểm %) | Ngôn ngữ nào người ta muốn dùng nhiều hơn đang dùng |
| f4_1 | Q4 | B | all | Network, networkx `spring_layout(seed=42)` | Cạnh = cặp cùng xuất hiện ở ≥2% người trả lời và lift ≥1,5 (29 cạnh, 20 nút, 5 cụm); nút theo số người dùng. Đã đổi từ tiêu chí ≥10% vì tiêu chí đó chỉ còn 13 nút dính nhau (hairball) | Ngôn ngữ nào thường đi cùng nhau |
| f4_2 | Q4 | B | all | Sankey, `go.Sankey` | Top 7 ngôn ngữ "đang dùng" → "muốn dùng", chỉ vẽ luồng ≥45% người dùng X muốn dùng Y (15 luồng), bỏ luồng cùng ngôn ngữ | Người đang dùng X thường muốn dùng Y |
| f5_1 | Q5 | C | sal | Histogram + đường median | Phân phối lương, trục log | Lương lệch phải mạnh, median khác xa mean |
| f5_2 | Q5 | C | sal | Ridgeline, `joypy` | Lương theo 12 vai trò, sắp theo median | Phân phối lương khác nhau theo vai trò |
| f5_3 | Q5 | C | sal | Line + khoảng tin cậy | Median lương theo bin `WorkExp` | Lương tăng theo kinh nghiệm |
| f6_1 | Q6 | C | sal | Bar ngang top 15 | Median lương theo ngôn ngữ, kèm `n` và khoảng tin cậy | Median lương theo ngôn ngữ chưa tách khỏi quốc gia |
| f6_2 | Q6 | C | sal | Heatmap, seaborn | Median lương: 10 ngôn ngữ × 6 vai trò, ô <30 dòng tô riêng | Lương theo giao điểm ngôn ngữ và vai trò |
| f6_3 | Q6 | A | sal | Bar xếp chồng hoặc bar | R² tăng dần: quốc gia, thêm kinh nghiệm, thêm ngôn ngữ | Quốc gia giải thích phần lớn chênh lệch lương |
| f6_4 | Q6 | A | sal | Biểu đồ hệ số (coef plot) | Hệ số ngôn ngữ trong hồi quy `log(lương)` kèm khoảng tin cậy | Sau khi loại nước và kinh nghiệm, ngôn ngữ tác động nhỏ |
| f7_1 | Q7 | C | sal | Choropleth, plotly | Median lương 62 nước (≥30 dòng); Việt Nam viền nhấn | Lương khác biệt rất lớn giữa các nước |
| f7_2 | Q7 | C | sal | Bar xếp hạng | Top và bottom 15 nước, Việt Nam (31 dòng) đánh dấu "mẫu nhỏ" | Việt Nam đứng ở đâu trong bảng xếp hạng |
| f8_1 | Q8 | C | sal | Spider, plotly `Scatterpolar` | 3 vai trò × 4 trục (median lương, median `WorkExp`, % dùng AI hằng ngày, `JobSat` trung bình vì median chỉ nhận 7 hoặc 8); mỗi trục chia cho giá trị cao nhất để trục bắt đầu từ 0 | So sánh hồ sơ vai trò |
| f8_2 | Q8 | C | sal | Lollipop hoặc bar | Cùng 4 chỉ số, giá trị thật | Số chính xác đi kèm spider |
| f9_1 | Q9 | A | all | Wordcloud | `AIOpen` đã bỏ stopword | Kỹ năng mà người trả lời cho là còn giá trị |
| f9_2 | Q9 | A | all | Bảng tần suất | Top 20 từ khóa | Bối cảnh cho wordcloud |

Tổng 23 biểu đồ (3+3+2+2+3+4+2+2+2). Ứng viên 3 vai trò cho `f8_1` dựa trên số đo: AI/ML engineer (dùng AI hằng ngày cao nhất, 73,6%), Engineering manager (median lương cao nhất, khoảng 133.417 USD), Developer embedded (dùng AI hằng ngày thấp nhất, 29,5%); chốt lại sau khi xem dữ liệu trong notebook.

## 4. Ánh xạ sang slide (12 slide, chỉ Q1–Q8)

| Slide | Nội dung | Biểu đồ |
|---|---|---|
| 1 | Tiêu đề, nhóm | Không có |
| 2 | Bối cảnh, câu hỏi, đối tượng | Không có |
| 3 | Ai trả lời khảo sát | f1_3 (và f1_1 nhỏ) |
| 4 | Công nghệ đang dùng | f2_1, f2_2 |
| 5 | Muốn dùng và ngưỡng mộ | f3_1 |
| 6 | Hệ sinh thái | f4_1, f4_2 |
| 7 | Phân phối lương | f5_2, f5_3 |
| 8 | Công nghệ và lương | f6_3, f6_4 |
| 9 | Bản đồ lương và Việt Nam | f7_1 |
| 10 | So sánh vai trò | f8_1 |
| 11 | Thông điệp chính và đề xuất | Không có (chữ) |
| 12 | Hạn chế và Q&A | Không có |

Q9 chỉ ở báo cáo (quyết định của nhóm). Mỗi slide có tối đa 2 biểu đồ để người xem hiểu trong 5 giây.

## 5. Ánh xạ sang báo cáo (33 trang dự trù)

| Chương | Biểu đồ | Người viết |
|---|---|---|
| 1. Giới thiệu | Không có | D |
| 2. Dữ liệu và tiền xử lý | f1_1 đến f1_3 và bảng thiếu dữ liệu | A |
| 3. Xu hướng công nghệ | f2_1 đến f4_2 | B |
| 4. Mức lương | f5_1 đến f8_2 | C |
| 5. Câu chuyện tổng hợp | f9_1, f9_2 và liên kết các phát hiện | A |
| 6. Kết luận và hạn chế | Không có | D |

Hạn chế phải nêu trong báo cáo: tự khai báo, lệch chọn mẫu (nhiều Mỹ, Đức, Ấn Độ), lương USD danh nghĩa chưa điều chỉnh sức mua, chỉ có năm 2025 nên "xu hướng" chỉ là lát cắt, Việt Nam chỉ 31 dòng lương, `WorkExp` lớn hơn `YearsCode` ở khoảng 9% dòng.

## 6. Điều kiện nghiệm thu mỗi biểu đồ

1. Có tệp ảnh đúng mã, đúng kích thước, chú thích chân đủ nguồn, bộ lọc, `n`, đơn vị.
2. Tiêu đề nêu phát hiện dựa trên số liệu thật, không dùng tiêu đề giả thuyết ở mục 3 nếu số liệu không ủng hộ.
3. Có tệp `<mã>_note.txt` (nhận xét và insight).
4. Chạy lại notebook từ đầu vẫn ra đúng biểu đồ đó.
