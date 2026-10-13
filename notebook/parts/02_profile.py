# %% [markdown]
# ## 2. Q1 – Ai là người trả lời khảo sát?
# Mẫu khảo sát tự nguyện nên có thể lệch. Ba biểu đồ dưới đây cho biết người trả lời là ai, bao nhiêu tuổi và sống ở đâu,
# để đặt đúng giới hạn cho các kết luận phía sau. Với số lượng phản hồi, ta dùng biểu đồ cột (không dùng bản đồ vì đây là số tuyệt đối).

# %%
BRANCH_SHORT = (
    Label("I am a developer by profession", "Lập trình viên chuyên nghiệp"),
    Label("I am not primarily a developer, but I write code sometimes as part of my work/studies", "Viết code thỉnh thoảng"),
    Label("I am learning to code", "Đang học code"),
    Label("I code primarily as a hobby", "Code như sở thích"),
    Label("I used to be a developer by profession, but no longer am", "Từng là lập trình viên"),
    Label("I work with developers or my work supports developers but am not a developer by profession",
          "Làm việc cùng lập trình viên"),
)
AGE_ORDER = ("Under 18 years old", "18-24 years old", "25-34 years old", "35-44 years old", "45-54 years old",
             "55-64 years old", "65 years or older")
AGE_SHORT = (
    Label("Under 18 years old", "<18"), Label("18-24 years old", "18–24"), Label("25-34 years old", "25–34"),
    Label("35-44 years old", "35–44"), Label("45-54 years old", "45–54"), Label("55-64 years old", "55–64"),
    Label("65 years or older", "65+"),
)
TOP_COUNTRIES = 14


def fig_f1_1(df: pd.DataFrame):
    """f1_1: cơ cấu người trả lời theo mức độ gắn với nghề lập trình."""
    counts = df[Col.MAIN].value_counts()
    n = int(counts.sum())
    pct = (counts / n * 100).sort_values()
    names = [label_map(BRANCH_SHORT).get(k, k) for k in pct.index]
    top_name, top_pct = names[-1], pct.iloc[-1]
    note = Note(
        "f1_1", f"{fmt_pct(top_pct, 0)} người trả lời là lập trình viên chuyên nghiệp",
        f"Trong {fmt_int(n)} người trả lời, nhóm '{top_name}' có {fmt_int(counts.max())} người ({fmt_pct(top_pct)}). "
        f"Người đang học code chiếm {fmt_pct(pct[counts.index[counts.index.str.contains('learning')][0]])}.",
        "Phân tích lương chỉ dùng nhóm lập trình viên chuyên nghiệp, nên kết quả không đại diện cho sinh viên mới học.",
        source_line(n, "Toàn bộ người trả lời."), n)
    fig, ax = new_fig(note, left=0.30)
    colors = [Pal.accent if nm == top_name else Pal.neutral for nm in names]
    ax.barh(names, pct.to_numpy(), color=colors, height=BAR_HEIGHT)
    annotate_bars_h(ax, pct.to_numpy(), [fmt_pct(v) for v in pct])
    ax.set_xlabel("Tỷ lệ người trả lời (%)")
    ax.set_xlim(0, pct.max() * 1.15)
    export_table(pct.rename("pct").reset_index(), "f1_1")
    return fig, note


def fig_f1_2(df: pd.DataFrame):
    """f1_2: phân bố người trả lời theo nhóm tuổi."""
    counts = df[Col.AGE].value_counts()
    n = int(counts.sum())
    present = [a for a in AGE_ORDER if a in counts.index]
    pct = (counts[present] / n * 100)
    top_age = pct.idxmax()
    short = label_map(AGE_SHORT)
    note = Note(
        "f1_2", f"Nhóm tuổi {short[top_age]} chiếm {fmt_pct(pct.max(), 0)} người trả lời",
        f"Hai nhóm {short[pct.nlargest(2).index[0]]} và {short[pct.nlargest(2).index[1]]} cộng lại chiếm {fmt_pct(pct.nlargest(2).sum())}. "
        f"Người từ 55 tuổi trở lên chỉ chiếm {fmt_pct(pct[[a for a in present if a.startswith(('55', '65'))]].sum())}.",
        "Mẫu trẻ và đang làm việc, phù hợp với đối tượng sinh viên và lập trình viên mới, nhưng thiếu tiếng nói của người lớn tuổi.",
        source_line(n, "Toàn bộ người trả lời; nhóm 'Prefer not to say' không vẽ nhưng vẫn nằm trong mẫu số."), n)
    fig, ax = new_fig(note, left=0.09)
    colors = [Pal.accent if a == top_age else Pal.neutral for a in present]
    ax.bar([short[a] for a in present], pct.to_numpy(), color=colors)
    for idx, val in enumerate(pct):
        ax.text(idx, val + PCT_PAD, fmt_pct(val), ha="center", fontsize=8)
    ax.set_ylabel("Tỷ lệ người trả lời (%)")
    ax.set_xlabel("Nhóm tuổi")
    export_table(pct.rename("pct").reset_index(), "f1_2")
    return fig, note


def fig_f1_3(df: pd.DataFrame):
    """f1_3: số phản hồi theo nước, Việt Nam được tô màu nhấn phụ."""
    answered = df[Col.COUNTRY].dropna()
    counts = answered.value_counts()
    n = len(answered)
    top = counts.head(TOP_COUNTRIES)
    vn = int(counts.get(VIETNAM, 0))
    top3 = ", ".join(short_country(c) for c in counts.index[:3])
    share3 = counts.head(3).sum() / n * 100
    note = Note(
        "f1_3", f"Mẫu lệch về {top3}; Việt Nam chỉ có {fmt_int(vn)} phản hồi",
        f"Ba nước đầu ({top3}) chiếm {fmt_pct(share3)} trong {fmt_int(n)} người có khai báo nước. "
        f"Việt Nam có {fmt_int(vn)} phản hồi ({fmt_pct(vn / n * 100, 2)}), xếp thứ {int(counts.index.get_loc(VIETNAM)) + 1} trong {len(counts)} nước.",
        "Kết luận về lương và công nghệ chủ yếu phản ánh Mỹ và châu Âu; số liệu Việt Nam chỉ mang tính tham khảo vì mẫu nhỏ.",
        source_line(n, "Người có khai báo nước."), n)
    labels = [short_country(c) for c in top.index] + ["…", short_country(VIETNAM)]
    values = list(top.to_numpy()) + [0, vn]
    fig, ax = new_fig(note, left=0.20)
    colors = [Pal.accent] * len(top) + [Pal.light, Pal.accent2]
    ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=BAR_HEIGHT)
    for idx, val in enumerate(values[::-1]):
        if val:
            ax.text(val + counts.max() * 0.01, idx, fmt_int(val), va="center", fontsize=8)
    ax.set_xlabel("Số phản hồi")
    thousands_axis(ax)
    export_table(counts.rename("count").reset_index(), "f1_3")
    return fig, note


# %%
finish(*fig_f1_1(df_all))

# %%
finish(*fig_f1_2(df_all))

# %%
finish(*fig_f1_3(df_all))
