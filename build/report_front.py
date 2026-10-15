"""Nội dung các trang đầu báo cáo: danh sách thành viên, phân công nhiệm vụ, thuật ngữ."""
from dataclasses import dataclass

from docx_front import Grid


@dataclass(frozen=True)
class Task:
    """Một nhiệm vụ của dự án."""
    name: str
    desc: str
    owner: str


@dataclass(frozen=True)
class Term:
    """Một thuật ngữ: tên tiếng Việt, tiếng Anh và giải nghĩa."""
    vi: str
    en: str
    meaning: str


def member_grid(members: tuple, title: str) -> Grid:
    """Bảng danh sách thành viên kèm số điện thoại và vai trò."""
    rows = [[str(idx), m.name, m.sid, m.phone, m.role] for idx, m in enumerate(members, start=1)]
    return Grid(title, ["STT", "Họ và tên", "Mã sinh viên", "Số điện thoại", "Vai trò"], rows, [1, 3, 2, 2, 2])


def task_grids(members: tuple, title: str) -> list:
    """Bảng phân công nhiệm vụ và bảng đánh giá đóng góp (hoàn thành đủ, đóng góp chia đều)."""
    duy, viet_huy, hung, ba_huy, done = "23010772", "23010699", "23010123", "23010806", "100%"
    tasks = (
        Task("Thu thập và mô tả dữ liệu", "Tải khảo sát Stack Overflow 2025, mô tả các biến và dữ liệu thiếu", duy),
        Task("Tiền xử lý dữ liệu", "Làm sạch theo quy tắc cố định, lọc lương hợp lệ, nhóm kinh nghiệm", duy),
        Task("Phân tích xu hướng công nghệ", "Mức dùng, mức ngưỡng mộ và mạng ngôn ngữ dùng chung", hung),
        Task("Phân tích mức lương", "Lương theo vai trò, kinh nghiệm, quốc gia và mô hình hồi quy", viet_huy),
        Task("AI, kỹ năng và câu chuyện dữ liệu", "Phân tích mức dùng AI, từ khóa kỹ năng và tổng hợp thông điệp", ba_huy),
        Task("Làm slide thuyết trình", "Thiết kế và hoàn thiện slide trình bày toàn bộ nội dung", ba_huy),
        Task("Tổng hợp và chỉnh sửa báo cáo", "Ghép nội dung, kiểm tra định dạng, rà soát toàn bộ báo cáo", viet_huy),
    )
    task_rows = [[str(idx), t.name, t.desc] for idx, t in enumerate(tasks, start=1)]
    share = f"{100 / len(members):g}%"
    share_rows = [[str(idx), m.name, "; ".join(t.name for t in tasks if t.owner == m.sid), done, share]
                  for idx, m in enumerate(members, start=1)]
    return [
        Grid(title, ["STT", "Nhiệm vụ", "Mô tả"], task_rows, [1, 4, 6]),
        Grid("", ["STT", "Thành viên", "Nhiệm vụ", "Đánh giá hoàn thành", "Tỷ lệ đóng góp toàn dự án"], share_rows, [1, 3, 3, 2, 2]),
    ]


def term_grid(title: str) -> Grid:
    """Bảng thuật ngữ dùng trong báo cáo."""
    terms = (
        Term("Trung vị", "Median", "Giá trị nằm chính giữa khi sắp xếp dữ liệu; ít bị ảnh hưởng bởi giá trị ngoại lệ hơn trung bình"),
        Term("Trung bình", "Mean", "Tổng các giá trị chia cho số quan sát"),
        Term("Khoảng tin cậy", "Confidence interval", "Khoảng giá trị có khả năng chứa tham số thật với mức tin cậy cho trước"),
        Term("Bootstrap", "Bootstrap", "Lấy mẫu lặp lại có hoàn lại từ dữ liệu để ước lượng độ bất định của một thống kê"),
        Term("Hệ số xác định", "R²", "Tỷ lệ biến thiên của biến phụ thuộc được mô hình hồi quy giải thích"),
        Term("Hồi quy tuyến tính", "Linear regression", "Mô hình ước lượng quan hệ tuyến tính giữa biến phụ thuộc và các biến giải thích"),
        Term("Tương quan hạng Spearman", "Spearman correlation", "Mức độ hai biến cùng tăng hoặc cùng giảm theo thứ hạng"),
        Term("Ước lượng mật độ hạt nhân", "Kernel density estimation (KDE)", "Đường cong trơn ước lượng phân bố của một biến số"),
        Term("Chỉ số lift", "Lift", "Tỷ số giữa tần suất hai mục cùng xuất hiện và tần suất kỳ vọng nếu chúng độc lập"),
        Term("Kể chuyện bằng dữ liệu", "Data storytelling", "Trình bày phát hiện từ dữ liệu thành mạch câu chuyện có thông điệp rõ ràng"),
    )
    return Grid(title, ["Thuật ngữ", "Tiếng Anh", "Giải nghĩa"], [[t.vi, t.en, t.meaning] for t in terms], [3, 2, 5])
