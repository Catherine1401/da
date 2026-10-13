# %% [markdown]
# ## 8. Tóm tắt phát hiện, khuyến nghị và hạn chế
# Các con số quan trọng được gom vào `out/tables/summary.json` để slide và báo cáo dùng đúng cùng số liệu với notebook.

# %%
ADM_MIN_USE = 5.0
TOP_RECS = 3


@dataclass
class Summary:
    """Các số liệu và thông điệp chính của đồ án."""
    n_all: int
    n_sal: int
    pct_pro: float
    median_pay: float
    mean_pay: float
    n_countries: int
    top_country: str
    top_country_median: float
    low_country: str
    low_country_median: float
    vn_rank: int
    vn_median: float
    vn_n: int
    r2_country: float
    r2_country_exp: float
    r2_full: float
    r2_language: float
    f_pvalue: float
    median_0_2: float
    median_21: float
    top_langs: list
    admired_langs: list
    rising_langs: list
    problem_solving_pct: float
    critical_thinking_pct: float
    ai_daily_pct: float
    ai_daily_pct_n: int
    spider_roles: list
    message: str
    recommendations: list
    limitations: list


def build_summary() -> Summary:
    """Tổng hợp số liệu từ các bảng đã tính trong notebook."""
    r2 = reg.r2.set_index("model").r2
    exp_table = median_table(df_sal.dropna(subset=[Col.EXPBIN]), Col.EXPBIN, with_ci=False).set_index(Col.EXPBIN)["median"]
    vn = by_country[by_country[Col.COUNTRY] == VIETNAM].iloc[0]
    pct_have, _ = share_answered(df_all, Col.LANG_HAVE)
    admired = lang[lang.have_pct >= ADM_MIN_USE].admired_pct.nlargest(TOP_RECS)
    rising = lang.want_gap.nlargest(TOP_RECS)
    ps_pct, ct_pct = phrase_share(open_texts, PHRASE_PROBLEM), phrase_share(open_texts, PHRASE_CRITICAL)
    ai_answered = df_all[Col.AI].dropna()
    ai_share = float((ai_answered == AI_DAILY).mean() * 100)
    first, last = exp_table.iloc[0], exp_table.iloc[-1]
    message = (f"Lương gắn với quốc gia và kinh nghiệm nhiều hơn với ngôn ngữ: quốc gia giải thích {fmt_pct(r2.iloc[2] * 100, 0)} biến thiên log(lương), "
               f"thêm kinh nghiệm lên {fmt_pct(r2.iloc[3] * 100, 0)}, thêm {REG_LANGS} ngôn ngữ chỉ cộng {fmt_num((r2.iloc[4] - r2.iloc[3]) * 100)} điểm phần trăm.")
    recs = [
        f"Bắt đầu từ nhóm ngôn ngữ phổ biến ({', '.join(pct_have.index[:3])}) vì có nhiều người dùng nhất trong mẫu khảo sát.",
        f"Theo dõi các ngôn ngữ đang được muốn dùng vượt mức đang dùng ({', '.join(rising.index)}) và các ngôn ngữ được ngưỡng mộ cao ({', '.join(admired.index)}) như hướng học thêm sau khi đã có nền tảng.",
        f"Đặt kỳ vọng lương theo kinh nghiệm: median nhóm 0–2 năm là {fmt_usd(first)}, nhóm 21+ năm là {fmt_usd(last)}; số liệu Việt Nam (median {fmt_usd(vn['median'])}, n = {int(vn['n'])}) chỉ mang tính tham khảo.",
        f"Làm quen với công cụ AI: {fmt_pct(ai_share, 0)} người trả lời dùng AI hằng ngày; cụm 'problem solving' xuất hiện trong {fmt_pct(ps_pct)} và 'critical thinking' trong {fmt_pct(ct_pct)} câu trả lời về kỹ năng còn giá trị.",
    ]
    limits = [
        "Dữ liệu tự khai báo và lệch chọn mẫu (nhiều người từ Mỹ, Đức, Ấn Độ), không đại diện cho toàn bộ thị trường lao động.",
        "Lương là USD danh nghĩa, chưa điều chỉnh sức mua; chỉ giữ lương trong khoảng 1.000–500.000 USD và lập trình viên chuyên nghiệp.",
        "Chỉ có năm 2025 nên 'xu hướng' được thay bằng ba chỉ số: đang dùng, muốn dùng, được ngưỡng mộ; không đo được thay đổi theo thời gian.",
        f"Việt Nam chỉ có {int(vn['n'])} dòng lương nên kết quả chỉ mang tính tham khảo.",
        "Hồi quy là mô hình mô tả, không chứng minh quan hệ nhân quả; số năm kinh nghiệm làm việc lớn hơn số năm lập trình ở khoảng 9% dòng có cả hai cột.",
    ]
    return Summary(
        n_all=len(df_all), n_sal=len(df_sal), pct_pro=float((df_all[Col.MAIN] == Cfg.pro_branch).mean() * 100),
        median_pay=float(df_sal[Col.SAL].median()), mean_pay=float(df_sal[Col.SAL].mean()), n_countries=len(by_country),
        top_country=short_country(by_country.iloc[0][Col.COUNTRY]), top_country_median=float(by_country.iloc[0]["median"]),
        low_country=short_country(by_country.iloc[-1][Col.COUNTRY]), low_country_median=float(by_country.iloc[-1]["median"]),
        vn_rank=int(by_country.index[by_country[Col.COUNTRY] == VIETNAM][0]) + 1, vn_median=float(vn["median"]), vn_n=int(vn["n"]),
        r2_country=float(r2.iloc[2]), r2_country_exp=float(r2.iloc[3]), r2_full=float(r2.iloc[4]), r2_language=float(r2.iloc[0]),
        f_pvalue=reg.f_pvalue, median_0_2=float(first), median_21=float(last), top_langs=list(pct_have.index[:3]),
        admired_langs=list(admired.index), rising_langs=list(rising.index), problem_solving_pct=ps_pct, critical_thinking_pct=ct_pct, ai_daily_pct=ai_share, ai_daily_pct_n=len(ai_answered), spider_roles=picked_roles,
        message=message, recommendations=recs, limitations=limits)


# %%
summary = build_summary()
(PATHS.tables / "summary.json").write_text(json.dumps(asdict(summary), ensure_ascii=False, indent=1), encoding="utf-8")
display(Markdown("**Thông điệp chính.** " + summary.message))
display(Markdown("**Khuyến nghị cho sinh viên và lập trình viên mới ở Việt Nam**\n\n" + "\n".join(f"{i}. {r}" for i, r in enumerate(summary.recommendations, 1))))
display(Markdown("**Hạn chế**\n\n" + "\n".join(f"- {r}" for r in summary.limitations)))

# %%
print("Ảnh đã lưu:", len(list(PATHS.figs.glob("*.png"))), "| Bảng và chú giải:", len(list(PATHS.tables.glob("*"))))
