# Kế hoạch đồ án: Phân tích xu hướng công nghệ và mức lương lập trình viên (Stack Overflow Developer Survey 2025)

Môn CSE702060 – Trực quan hóa dữ liệu (Phenikaa). Nhóm 8. Đồ án lớn chiếm 60% điểm kết thúc học phần.
Tài liệu này chỉ gồm requirement, thiết kế, plan và setup môi trường. Chưa có dòng code nào của đồ án.

## 1. Requirement đã chốt

| Mục | Nội dung | Nguồn |
|---|---|---|
| Đề tài | Phân tích xu hướng công nghệ và mức lương lập trình viên qua khảo sát Stack Overflow 2025 | `docs/bienbanhopnhomlan1.docx` |
| Dữ liệu | `results.csv` (49.191 dòng × 172 cột) và `schema.csv` (139 dòng mô tả) của năm 2025 | `docs/intent.md`, đã tải về `data/` |
| Sản phẩm 1 | 1 file `.ipynb` tự chứa, đã chạy sẵn kết quả | `intent.md` + quyết định của người dùng |
| Sản phẩm 2 | 1 bộ slide thuyết trình, đúng 12 slide | `intent.md` |
| Sản phẩm 3 | 1 báo cáo `.docx`, tối thiểu 30 trang | `intent.md` |
| Ngôn ngữ | Tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh | quyết định của người dùng |
| Dashboard Streamlit | Không làm | quyết định của người dùng |
| Xu hướng | Chỉ dùng 2025, lấy "đang dùng / muốn dùng / được ngưỡng mộ" làm chỉ số thay thế | quyết định của người dùng |
| Cách sinh slide, docx | Script `python-pptx`, `python-docx` dựng từ cùng bộ biểu đồ PNG của notebook | quyết định của người dùng |
| Rubric của giảng viên | Không có (người dùng xác nhận). Tiêu chí lấy từ bài giảng, quy ước ở mục 3b (giả định, xem mục 11) | người dùng |
| Hạn nộp | 15/10/2026 (thứ Năm); giờ nộp và hình thức nộp chưa biết | người dùng |
| Nhóm | 4 người: Lê Đức Duy, Vũ Viết Huy, Lê Mạnh Hùng, Nguyễn Bá Huy | người dùng + biên bản họp |

Điểm lệch cần nhóm biết:
- Giáo trình ghi "Bài tập lớn – Nhóm 3 người", nhưng nhóm có 4 người (người dùng xác nhận). Plan chia việc cho 4 người.
- Biên bản họp có nhắc "xây dựng biểu đồ và dashboard", nhưng `intent.md` và người dùng chọn không làm dashboard. Plan theo `intent.md`.

## 2. Sự thật về dữ liệu (đã đo, không phải phỏng đoán)

| Phát hiện | Số liệu | Hệ quả thiết kế |
|---|---|---|
| Không có cột năm | File chỉ có năm 2025 | "Xu hướng" chỉ là lát cắt, phải nói rõ hạn chế trong báo cáo |
| `ConvertedCompYearly` là lương quy đổi USD | 6.319 dòng có `Currency` bắt đầu bằng USD: `CompTotal == ConvertedCompYearly` ở 6.319/6.319 dòng có cả hai giá trị (còn 228 dòng USD có `CompTotal = 0` và `ConvertedCompYearly` rỗng); các tiền tệ khác (EUR, UAH) được quy đổi | Dùng cột này làm lương chung |
| Lương lệch rất mạnh | Mean 101.762 USD, median 75.320 USD, std 461.700, max 50 triệu | Dùng median, không dùng mean |
| Lương cần lọc ngoại lai | 23.947 dòng có lương; 724 dòng dưới 1.000 USD; 46 dòng trên 1 triệu USD; còn 23.044 dòng (96,2%) trong khoảng 1.000–500.000 USD | Quy tắc lọc: giữ 1.000–500.000 USD, ghi rõ trong báo cáo |
| Cột chọn nhiều đáp án | Phân tách bằng `;`, ví dụ `Dart;HTML/CSS;JavaScript;TypeScript`. Có 42 ngôn ngữ, 30 CSDL, 42 nền tảng cloud, 28 web framework, 17 mô hình AI, 27 môi trường dev | Cần bước tách (explode) và bảng 0/1 |
| `Admired` là tập con của `HaveWorkedWith` | 100% dòng đúng cho Language và Database | Tính "tỷ lệ ngưỡng mộ" = Admired / HaveWorkedWith |
| Thiếu dữ liệu nhiều | Chỉ 8 cột đầy ≥90%; 93 cột 50–90%; 71 cột dưới 50% | Mỗi biểu đồ phải ghi `n` mẫu thực dùng |
| Mẫu theo quốc gia | Tính trên bảng lương đã áp đủ quy tắc mục 4 (19.576 dòng): 62 nước ≥30 dòng lương, 36 nước ≥100. Việt Nam: 145 phản hồi, chỉ 31 dòng có lương (vừa chạm ngưỡng 30). Trước khi lọc "chuyên nghiệp": 66 nước, 41 nước, 37 dòng | Choropleth dùng nước ≥30; Việt Nam sát ngưỡng nên ghi "mẫu nhỏ", nếu đổi quy tắc lọc có thể rơi khỏi bản đồ |
| Mẫu theo vai trò | Trên bảng 19.576 dòng, `DevType` có 13 nhóm ≥200 dòng lương, còn 12 nhóm sau khi bỏ "Other (please specify)" (trước khi lọc chuyên nghiệp: 18 và 17). Top trước khi lọc chuyên nghiệp: full-stack 7.215, back-end 3.815, architect 1.589 | Ridgeline và spider chỉ dùng nhóm ≥200 |
| Kinh nghiệm là số | `YearsCode`, `WorkExp` không có giá trị chữ | Không cần chuẩn hóa chuỗi, chỉ chia nhóm bin |
| Tên nước không khớp ISO | `pycountry` không nhận 14 tên: Iran, Turkey, Hong Kong, Republic of Korea, Venezuela, Kosovo, Swaziland, Palestine, Congo (2 tên), Micronesia, Libya, Cape Verde, "Nomadic" | Cần bảng alias thủ công; "Nomadic" loại khỏi bản đồ |
| Nhóm lọc người trả lời | 37.467 là lập trình viên chuyên nghiệp; 4.894 viết code thỉnh thoảng; 2.585 đang học | Phân tích lương chỉ dùng "I am a developer by profession" (20.195 dòng có lương trước khi lọc ngoại lai, 19.576 dòng sau khi lọc) |

Sau khi áp đủ quy tắc lọc ở mục 4 (lương 1.000–500.000 USD và lập trình viên chuyên nghiệp: 19.576 dòng), số dòng có đủ trường dùng để cắt chéo: Country 19.576, DevType 19.576, YearsCode 19.516, WorkExp 19.381, AISelect 19.085, Language 18.331, RemoteWork 17.506, JobSat 18.870 (`JobSat` có 0 dòng ngoài nhóm chuyên nghiệp).

## 3. Thông điệp chính và câu hỏi phân tích

Danh mục 22 biểu đồ cụ thể (mã, người làm, dữ liệu, tiêu đề nháp), quy ước màu, kích thước ảnh và kết quả đo khả thi nằm ở `design.md`.

Công thức của môn: Câu chuyện dữ liệu = Dữ liệu + Trực quan hóa + Bối cảnh + Trình tự + Thông điệp.

Đo thử sơ bộ (chưa phải kết quả cuối): hồi quy `log(lương)` cho R² 0,450 khi chỉ có quốc gia, 0,523 khi thêm kinh nghiệm, 0,548 khi thêm 15 ngôn ngữ phổ biến nhất (chi tiết và hạn chế ở `design.md` mục 1).

Thông điệp dự kiến (nháp, phải kiểm chứng bằng dữ liệu rồi mới chốt): công nghệ đang được dùng nhiều chưa chắc là công nghệ được ngưỡng mộ hay mang lại lương cao; lương phụ thuộc vào quốc gia và kinh nghiệm hơn là vào bản thân ngôn ngữ lập trình.

| # | Câu hỏi | Biến chính | Dạng biểu đồ (theo các bài giảng của môn) |
|---|---|---|---|
| Q1 | Ai là người trả lời khảo sát? Mẫu có lệch không? | `MainBranch`, `Age`, `Country`, `DevType`, `EdLevel` | Bar xếp hạng, histogram. Không dùng choropleth cho số phản hồi vì bài giảng cấm dữ liệu tuyệt đối trên bản đồ |
| Q2 | Công nghệ nào đang được dùng nhiều nhất? | `Language/Database/Platform/Webframe HaveWorkedWith` | Bar ngang, treemap bằng `px.treemap` (nhóm → công nghệ); số chính xác kèm bar hoặc bảng |
| Q3 | Công nghệ nào được muốn dùng và được ngưỡng mộ so với đang dùng? | `*WantToWorkWith`, `*Admired`, `*HaveWorkedWith` | Scatter (dùng vs ngưỡng mộ), diverging bar, slopegraph |
| Q4 | Các công nghệ đi cùng nhau thế nào? Người đang dùng X thường muốn dùng Y? (chỉ là "muốn dùng" tại một thời điểm, không phải chuyển đổi thực tế) | Cặp cột `HaveWorkedWith` và `WantToWorkWith` | Network `networkx` (đồng xuất hiện, chỉ giữ cạnh trọng số cao, `spring_layout(seed=42)`), adjacency matrix (heatmap) nếu mạng dày, Sankey `go.Sankey` ("đang dùng" → "muốn dùng") |
| Q5 | Phân phối lương theo vai trò và kinh nghiệm ra sao? | `ConvertedCompYearly`, `DevType`, `YearsCode` | Ridgeline bằng `joypy` (đã cài), box, line median theo năm kinh nghiệm kèm khoảng tin cậy |
| Q6 | Công nghệ nào đi cùng mức lương cao, sau khi loại ảnh hưởng của nước và kinh nghiệm? | Lương × ngôn ngữ, CSDL, cloud; `Country`, `WorkExp` | Bar median, heatmap (công nghệ × vai trò), biểu đồ hệ số hồi quy `log(lương)` |
| Q7 | Lương khác nhau thế nào giữa các nước, Việt Nam đứng đâu? | `Country`, lương | Choropleth median lương, bar xếp hạng. Lương là USD danh nghĩa, chưa điều chỉnh sức mua; phải ghi rõ khi nói vị trí Việt Nam |
| Q8 | So sánh nhiều chiều giữa các vai trò? | Lương median, `WorkExp` median, tỷ lệ dùng AI hằng ngày, `JobSat` median (4 trục, bỏ remote) | Spider chart: dưới 5 trục, mỗi hình ≤3 vai trò (nhiều hơn thì tách small multiples), thứ tự trục cố định; chuẩn hóa 0–1 nhưng ghi giá trị thật trên từng trục; kèm bar hoặc lollipop để đọc số chính xác |
| Q9 | Kỹ năng nào người trả lời cho là còn giá trị sau 3–5 năm? | `AIOpen` (22.540 câu trả lời văn bản) | Wordcloud bỏ stopword, từ quá dài hoặc quá ngắn; kèm bảng tần suất để có bối cảnh |

Q9 gắn với "xu hướng" ở khía cạnh AI. Quyết định: giữ Q9 trong notebook và báo cáo, không đưa vào slide (slide chỉ phủ Q1–Q8, nên slide và báo cáo không phủ cùng nội dung).

Kiểm chứng thông điệp (quyết định): thêm mô hình hồi quy `log(lương) ~ quốc gia + kinh nghiệm + ngôn ngữ` bằng `statsmodels` để tách ảnh hưởng của nước và kinh nghiệm khỏi ngôn ngữ; kết quả quyết định thông điệp chính được giữ, sửa hay bỏ. Nếu hồi quy bác bỏ giả thuyết, thông điệp phải đổi theo dữ liệu.

Ghi chú về suy luận: khảo sát là tự khai báo, có thể lệch chọn (mẫu nhiều từ Mỹ, Đức, Ấn Độ). Chỉ trình bày tương quan, không kết luận nhân quả.

### 3b. Quy ước trình bày rút ra từ bài giảng

Nguồn: các PDF trong `docs/` đã đọc xong (Choropleth, Heatmap, Ridgeline, Spider, WordCloud, bài 2, 3, 6, 9). Bài giảng không có tiêu chí chấm đồ án.

| Chủ đề | Quy ước áp dụng |
|---|---|
| Đối tượng và mục tiêu (quyết định) | Sinh viên và dev mới ở Việt Nam. Mẫu: "Sau khi xem sản phẩm, sinh viên và dev mới ở Việt Nam sẽ hiểu rằng [phát hiện chính], từ đó có thể [chọn công nghệ học và kỳ vọng lương]". Điền phát hiện sau khi hồi quy xong |
| Cấu trúc câu chuyện | Bối cảnh → Vấn đề → Phát hiện → Bằng chứng → Kết luận hoặc khuyến nghị; thứ tự biểu đồ từ rộng đến hẹp |
| Thăm dò và giải thích | Notebook là phân tích khám phá (được nhiều biểu đồ); slide và báo cáo là phân tích giải thích (chỉ biểu đồ quan trọng nhất) |
| Tiêu đề biểu đồ | Cấp 2 (nêu phát hiện) hoặc cấp 3 (định hướng quyết định), không dùng tiêu đề chỉ mô tả |
| Màu | Phần lớn màu xám trung tính, 1–2 màu nhấn, cùng một màu cho cùng một ý trên mọi biểu đồ; không chỉ dùng màu để mã hóa (thêm nhãn, ký hiệu); bảng màu an toàn cho người mù màu; không dùng 3D |
| Chú thích và tham chiếu | Chú thích ngắn gần dữ liệu; đường tham chiếu (ví dụ median toàn mẫu) có nhãn trực tiếp |
| Độ không chắc chắn | Ghi `n` trên mỗi biểu đồ, ghi dữ liệu thiếu, dùng khoảng tin cậy bootstrap cho median lương; dùng câu thận trọng ("đi cùng", không "làm tăng") |
| Phát hiện và ý kiến | Phát hiện có phạm vi và `n` rõ, kiểm chứng được; suy đoán đánh dấu là suy đoán |
| Choropleth | Chỉ dùng dữ liệu chuẩn hóa (median lương), một biến, bảng màu tuần tự, thang liên tục, có tooltip |
| Heatmap | Ô thiếu dữ liệu tô màu riêng, không tô như 0; có số trong ô khi ít ô |
| Network | Chỉ giữ cạnh trọng số cao để tránh hairball; "bậc cao ≠ quan trọng"; ghi bố cục chỉ để quan sát; kèm bar hoặc bảng cho số chính xác |
| Pie | Chỉ khi ≤5 nhóm; mặc định dùng bar |
| Mỗi biểu đồ | Kèm đoạn nhận xét và insight (bài tập của môn đều yêu cầu "đánh giá nội dung hình vẽ") |

## 4. Quy tắc làm sạch dữ liệu (cố định để 3 sản phẩm cùng số liệu)

1. Đọc CSV bằng `utf-8-sig` (file có BOM).
2. Bảng lương: giữ `ConvertedCompYearly` trong 1.000–500.000 USD; chỉ dùng người có `MainBranch` = "I am a developer by profession".
3. Cột chọn nhiều đáp án: tách theo `;`, tính tỷ lệ trên số người có trả lời ở cột đó (không chia cho toàn bộ 49.191).
4. Nhóm quốc gia chỉ đưa vào so sánh khi có ≥30 dòng lương; ghi `n` trên biểu đồ.
5. `DevType` giữ nhóm ≥200 dòng lương; bỏ nhóm "Other (please specify)".
6. Quy đổi tên nước sang ISO-3 bằng `pycountry` cộng bảng alias thủ công cho 13 tên đã liệt kê.
7. Kinh nghiệm dùng cột `WorkExp` (quyết định), không loại dòng; chia bin 0–2, 3–5, 6–10, 11–20, 21+ năm (có thể chỉnh khi xem phân phối thật). `WorkExp` lớn hơn `YearsCode` ở 3.564/39.869 dòng có cả hai (khoảng 9%, mâu thuẫn logic), phải nêu trong báo cáo.
8. Mọi biểu đồ ghi nguồn, `n`, bộ lọc đã áp dụng.

## 5. Thiết kế notebook (`so2025.ipynb`, tự chứa)

Mỗi hàm ≤100 dòng, một việc một hàm; mỗi ô một ý. Tên biến, hằng số khai báo ở phạm vi hẹp nhất, mọi literal là hằng có tên. Chú thích code bằng tiếng Việt, một dòng.

| Phần | Nội dung |
|---|---|
| 0 | Tiêu đề, mục tiêu, cách chạy |
| 1 | Cấu hình: đường dẫn, hằng số lọc, bảng màu |
| 2 | Tải dữ liệu, kiểm tra schema, báo cáo thiếu dữ liệu |
| 3 | Làm sạch: lọc lương, tách cột nhiều đáp án, ánh xạ ISO-3 |
| 4 | Q1 hồ sơ người trả lời |
| 5 | Q2–Q4 xu hướng công nghệ |
| 6 | Q5–Q8 lương, gồm hồi quy `log(lương)` ở Q6 |
| 7 | Q9 AI và kỹ năng tương lai |
| 8 | Tóm tắt phát hiện, hạn chế |
| 9 | Xuất toàn bộ PNG sang `out/figs/` và bảng số sang `out/tables/` |

Điều kiện nghiệm thu: `jupyter nbconvert --to notebook --execute` chạy hết từ đầu không lỗi; mọi ô có output; thời gian chạy ghi lại; không phụ thuộc file ngoài `data/`.

## 6. Thiết kế slide (đúng 12)

1. Tiêu đề, nhóm, thành viên
2. Bối cảnh và câu hỏi nghiên cứu
3. Dữ liệu: ai trả lời (Q1)
4. Công nghệ đang dùng (Q2)
5. Muốn dùng và ngưỡng mộ so với đang dùng (Q3)
6. Hệ sinh thái: mạng đồng xuất hiện và dòng "đang dùng → muốn dùng" (Q4)
7. Phân phối lương theo vai trò và kinh nghiệm (Q5)
8. Công nghệ nào đi cùng lương cao (Q6)
9. Bản đồ lương và vị trí Việt Nam (Q7)
10. So sánh vai trò (Q8)
11. Thông điệp chính và đề xuất
12. Hạn chế và Q&A

Slide chỉ phủ Q1–Q8; Q9 chỉ nằm trong notebook và báo cáo. Slide 11 chỉ trình bày thông điệp chính và đề xuất.

Quy ước: mỗi slide một thông điệp ở tiêu đề (không phải nhãn chung chung), 5 giây là hiểu (theo bài giảng Dashboard).

## 7. Thiết kế báo cáo docx (≥30 trang)

| Chương | Nội dung | Trang ước tính |
|---|---|---|
| Bìa, mục lục, tóm tắt | | 3 |
| 1. Giới thiệu | Bối cảnh, mục tiêu, câu hỏi | 3 |
| 2. Dữ liệu và tiền xử lý | Nguồn, schema, thiếu dữ liệu, quy tắc ở mục 4 | 5 |
| 3. Xu hướng công nghệ | Q1–Q4, mỗi biểu đồ kèm diễn giải | 7 |
| 4. Mức lương | Q5–Q8, gồm mô hình hồi quy và cách đọc hệ số | 8 |
| 5. Câu chuyện tổng hợp | Q9 và liên kết các phát hiện | 3 |
| 6. Kết luận và hạn chế | | 2 |
| Tài liệu tham khảo, phụ lục | Bảng số liệu | 2 |
| Tổng | | 33 (dự trù thêm phụ lục bảng số liệu để không phải độn trang nếu thiếu) |

Nghiệm thu: chuyển bằng LibreOffice sang PDF rồi đếm trang (`soffice --headless --convert-to pdf` + `pdfinfo`) để chứng minh ≥30 trang. Không có `pandoc`, nên docx dựng bằng `python-docx`.

## 8. Kiến trúc và cấu trúc thư mục

```
da/
  data/            results.csv, schema.csv (đã tải, `.gitignore` loại; thư mục chưa `git init`)
  docs/            bài giảng, intent.md, biên bản họp
  notebook/parts/  các phần nguồn của notebook (00_setup … 08_summary), mỗi file < 1000 dòng
  build/           make_nb.py (ghép và chạy notebook), build_pptx.py, build_docx.py (đọc out/, không tự xử lý dữ liệu)
  out/figs/        PNG do notebook xuất
  out/tables/      CSV tóm tắt cho báo cáo
  deliverables/    so2025.ipynb, slides.pptx, report.docx (bản nộp)
  requirements.txt
  plan.md
  design.md
```

Nguyên tắc: số liệu chỉ sinh ra ở notebook; hai script build chỉ đọc `out/` để slide, báo cáo, notebook luôn khớp nhau.

## 9. Môi trường (đã setup xong và kiểm chứng)

| Hạng mục | Kết quả đo |
|---|---|
| Môi trường | `venv` tại `.venv/` (không dùng conda), Python 3.10.12 của hệ thống, kernel Jupyter "Python (da)" trỏ tới `.venv` |
| Thư viện | pandas 2.3.3, numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.9, seaborn 0.13.2, plotly 7.1.0, networkx 3.4.2, scikit-learn 1.7.2, statsmodels 0.15.0, wordcloud 1.9.6, squarify 0.4.5 (không dùng, bài giảng dùng plotly), joypy 0.2.6, pycountry, python-docx 1.2.0, python-pptx 1.0.2, nbconvert 7.17.2, jupyterlab 4.6.4, kaleido 1.5.0 |
| Xuất ảnh plotly | Chạy thử `write_image` thành công (Chrome 155 có sẵn) |
| Dấu tiếng Việt trên biểu đồ | Font mặc định DejaVu Sans hiển thị đúng ằ, ơ, ư; không đổi font |
| Đếm trang docx | LibreOffice 7.3.7.2 có sẵn |
| Dữ liệu | `data/results.csv` 140.893.245 byte, `data/schema.csv` 30.403 byte |
| Đóng băng | `requirements.txt` (130 gói, gồm joypy) |
| Kích hoạt | `source .venv/bin/activate` hoặc gọi trực tiếp `.venv/bin/python` |
| Lưu ý | Python 3.10 khiến pip chọn pandas 2.x, numpy 2.2, scipy 1.15 (bản mới hơn cần Python ≥3.11); đủ cho đồ án |
| Ổ đĩa | Còn khoảng 16 GB |

## 10. Phân công (4 người)

Tên người nhận từng vai trò do nhóm tự gán; plan không tự chọn.

| Vai trò | Việc chính | Sản phẩm |
|---|---|---|
| A. Dữ liệu và hồi quy | Phần 0–3 của notebook (đọc, làm sạch, bảng alias nước, hàm tách cột nhiều đáp án), hồi quy `log(lương)`, Q9 | Bảng `df_sal`, hàm dùng chung, chương 2 và 5 của báo cáo |
| B. Công nghệ | Q1–Q4 | Biểu đồ phần 4–5, chương 3 của báo cáo |
| C. Lương | Q5–Q8 | Biểu đồ phần 6, chương 4 của báo cáo |
| D. Tổng hợp | Gộp notebook, `build_pptx.py`, `build_docx.py`, đếm trang, chương 1 và 6, luyện thuyết trình | Slide, báo cáo hoàn chỉnh |

Quy ước làm song song (chỉ có 1 notebook): mỗi người làm trong một notebook nháp riêng của mình (`part_a.ipynb`, `part_b.ipynb`, `part_c.ipynb`), D gộp vào `so2025.ipynb` rồi chạy `nbconvert --execute` từ đầu. Không ai sửa ô của người khác.

Hợp đồng dữ liệu để B và C làm được ngay mà không chờ A: bảng lương `df_sal` gồm đúng 19.576 dòng (quy tắc mục 4) với các cột `ResponseId`, `Country`, `iso3`, `DevType`, `WorkExp`, `exp_bin`, `salary_usd` (từ `ConvertedCompYearly`), `AISelect`, `RemoteWork`, `JobSat` và các cột chọn nhiều đáp án giữ nguyên chuỗi có dấu `;`. Hàm `explode_multi(df, col)` trả về bảng dạng dài. Q1–Q4 (B) không giới hạn ở người có lương: dùng thêm `df_all` (49.191 dòng, chưa lọc), với mẫu số là số người có trả lời cột đó (quy tắc 3 mục 4) và ghi `n` trên biểu đồ. Nếu `df_sal` của A khác số dòng 19.576 thì A đang sai quy tắc lọc.

## 10b. Lịch đến hạn 15/10 (hôm nay là 13/10 lúc 16:00)

Giờ nộp cuối cùng chưa biết; lịch này giả định phải xong trước cuối ngày 15/10, và dành sáng 15/10 làm dự phòng.

| Thời điểm | A | B | C | D |
|---|---|---|---|---|
| Tối 13/10 | `df_sal`, `explode_multi`, alias nước (xong trước khi B và C cần) | Viết hàm vẽ Q1–Q3 trên dữ liệu thô theo hợp đồng | Viết hàm vẽ Q5–Q7 trên dữ liệu thô | Dựng khung `build_pptx.py` và `build_docx.py` với ảnh giả, chương 1 |
| Ngày 14/10 sáng | Hồi quy `log(lương)`, Q9 | Q1–Q4 hoàn chỉnh | Q5–Q8 hoàn chỉnh | Gộp notebook, chạy `nbconvert --execute` (mốc 12:00) |
| Ngày 14/10 chiều | Chương 2 và 5, nhận xét biểu đồ | Chương 3, nhận xét biểu đồ | Chương 4, nhận xét biểu đồ | Slide 12 cái, ghép chương, build lần 1 và đếm trang (mốc tối) |
| Sáng 15/10 | Rà số liệu 3 sản phẩm | Rà biểu đồ, tiêu đề | Rà biểu đồ, tiêu đề | Build cuối, đếm trang ≥30, kiểm 12 slide, luyện thuyết trình |
| Còn lại 15/10 | Dự phòng và nộp | | | |

Nút thắt chính: viết nhận xét cho từng biểu đồ và 30 trang chữ, không phải code. Vì vậy mỗi người tự viết chương của mình ngay khi có biểu đồ, không đợi D.

Thứ tự cắt nếu trễ (cắt từ dưới lên):
1. Bắt buộc: notebook chạy đủ Q1–Q8 và hồi quy, 12 slide, docx ≥30 trang.
2. Nên có: Q9 wordcloud, Sankey, spider, khoảng tin cậy bootstrap.
3. Cắt trước: adjacency matrix, ridgeline thêm nhóm phụ, phụ lục bảng số liệu dài (chỉ cắt phụ lục khi đã đủ 30 trang bằng nội dung thật).

## 11. Giả định và điểm chưa chắc

| Giả định | Trạng thái |
|---|---|
| Tiêu chí chấm lấy từ bài giảng vì không có rubric | Đã xác nhận không có rubric; chấp nhận rủi ro này |
| Nội dung các PDF Choropleth, Heatmap, Ridgeline, Spider, WordCloud, bài 2, 3, 6, 9 | Đã đọc phần chữ (không đọc phần ảnh, code trong slide); kết quả ở mục 3b. Bài giảng không nêu tiêu chí chấm đồ án |
| Danh sách dạng biểu đồ trong mục 3 đủ để đạt điểm | Không xác nhận được (không có rubric); đã phủ các dạng trong bài giảng: bar, histogram, line, scatter, box, heatmap, ridgeline, spider, wordcloud, choropleth, treemap, network, Sankey |
| Giờ nộp và hình thức nộp ngày 15/10 | Chưa biết; nhóm cần xác nhận |
| Ngưỡng 30 dòng/nước và 200 dòng/vai trò | Do mình chọn, có thể chỉnh sau khi xem phân phối thật |
| Quy tắc lọc 1.000–500.000 USD | Do mình chọn, giữ 96,2% dòng; phải ghi trong báo cáo |
| Thông điệp chính ở mục 3 | Là giả thuyết, chưa kiểm chứng; đồ thị thật có thể bác bỏ |
| Notebook tự chứa 1 file có thể vượt giới hạn 1000 dòng | Giữ quyết định "1 file"; giới hạn tính theo dòng mã nguồn các ô, không tính JSON của output. Nếu vượt, báo cáo và xin quyết định tách module (ý kiến đánh giá ngoài khuyên tách) |
| Hạn chế "xu hướng chỉ trong 2025" | Đã chọn chấp nhận; nếu giảng viên đòi xu hướng theo thời gian thì phải thêm `2024/results.csv` (160 MB, đã xác nhận tồn tại trên GitHub) |

## 12. Trạng thái thực hiện (cập nhật 13/10/2026)

1. Đã xong: đọc các PDF bài giảng, quy ước ở mục 3b; rubric không có; hạn nộp 15/10; nhóm 4 người.
2. Đã xong: notebook `deliverables/so2025.ipynb` (53 ô code, chạy từ đầu không lỗi, 23 biểu đồ), `deliverables/slides.pptx` (12 slide), `deliverables/report.docx` (40 trang theo LibreOffice).
3. Đã kiểm chứng: một agent tự tính lại 24 chỉ số chính từ dữ liệu thô, tất cả khớp; một agent khác rà văn bản và các lỗi có bằng chứng đã được sửa.
4. Còn lại cho nhóm: xác nhận giờ nộp và hình thức nộp ngày 15/10, mở báo cáo trong Word để kiểm tra phân trang, luyện thuyết trình.
5. Chạy lại toàn bộ: `python build/make_nb.py`, `python build/build_pptx.py`, `python build/build_docx.py` (xem Phụ lục E của báo cáo).
