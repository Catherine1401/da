# %% [markdown]
# ## 5. Q8 – So sánh các vai trò
# Spider chart dễ gây hiểu nhầm (thứ tự trục ảnh hưởng hình dạng, diện tích phóng đại chênh lệch), nên ta giữ dưới 5 trục, chỉ so sánh 3 vai trò,
# chia mỗi trục cho giá trị cao nhất giữa các vai trò (trục bắt đầu từ 0 thật, không phóng đại chênh lệch) và đi kèm biểu đồ chấm có giá trị thật để đọc số chính xác.

# %%
@dataclass(frozen=True)
class Metric:
    """Một chỉ số của hồ sơ vai trò: tên cột kết quả, nhãn trục, đơn vị và số chữ số thập phân."""
    key: str
    label: str
    unit: str
    digits: int


METRICS = (
    Metric("median_sal", "Median lương", "USD", 0),
    Metric("median_exp", "Median kinh nghiệm", "năm", 0),
    Metric("ai_daily", "Dùng AI hằng ngày", "%", 0),
    Metric("mean_sat", "Hài lòng công việc (TB, 0–10)", "điểm", 1),
)
SPIDER_ROLES = 3
SPIDER_FILL_ALPHA = 0.25
SPIDER_LINE_WIDTH = 3
DOT_SIZE = 40
THOUSAND = 1000
CORR_WEAK = 0.3
CORR_STRONG = 0.6


def role_profile(df: pd.DataFrame, role_names: list) -> pd.DataFrame:
    """Hồ sơ 4 chỉ số cho từng vai trò."""
    rows = []
    for name in role_names:
        grp = df[df[Col.ROLE] == name]
        ai_answered = grp[Col.AI].dropna()
        rows.append({
            Col.ROLE: name, "n": len(grp),
            "median_sal": grp[Col.SAL].median(), "median_exp": grp[Col.WORKEXP].median(),
            "ai_daily": (ai_answered == AI_DAILY).mean() * 100, "mean_sat": grp[Col.JOBSAT].mean(),
        })
    return pd.DataFrame(rows)


def pick_spider_roles(profile: pd.DataFrame) -> list:
    """Chọn 3 vai trò tương phản: lương cao nhất, dùng AI nhiều nhất, dùng AI ít nhất."""
    picks = [profile.loc[profile.median_sal.idxmax(), Col.ROLE], profile.loc[profile.ai_daily.idxmax(), Col.ROLE],
             profile.loc[profile.ai_daily.idxmin(), Col.ROLE]]
    unique = list(dict.fromkeys(picks))
    rest = [r for r in profile.sort_values("n", ascending=False)[Col.ROLE] if r not in unique]
    return (unique + rest)[:SPIDER_ROLES]


def describe_corr(corr: float) -> str:
    """Diễn giải mức độ và chiều của hệ số tương quan."""
    strength = "gần như không liên hệ" if abs(corr) < CORR_WEAK else ("liên hệ vừa phải" if abs(corr) < CORR_STRONG else "liên hệ mạnh")
    direction = "" if abs(corr) < CORR_WEAK else (", cùng chiều" if corr > 0 else ", ngược chiều")
    return strength + direction


def scale_unit(profile: pd.DataFrame) -> pd.DataFrame:
    """Chia mỗi chỉ số cho giá trị cao nhất giữa các vai trò (0–1, trục bắt đầu từ 0 thật)."""
    keys = [m.key for m in METRICS]
    return profile[keys] / profile[keys].max()


def axis_text(metric: Metric, profile: pd.DataFrame) -> str:
    """Nhãn trục kèm dải giá trị thật (thấp nhất–cao nhất)."""
    lo, hi = profile[metric.key].min(), profile[metric.key].max()
    return f"{metric.label}<br>({fmt_num(lo, metric.digits)}–{fmt_num(hi, metric.digits)} {metric.unit})"


# %%
def fig_f8_1(profile: pd.DataFrame, picked: list):
    """f8_1: spider chart hồ sơ 3 vai trò trên 4 trục chuẩn hóa."""
    unit = scale_unit(profile)
    unit.index = profile[Col.ROLE]
    top_sal = profile.loc[profile.median_sal.idxmax()]
    top_ai = profile.loc[profile.ai_daily.idxmax()]
    low_ai = profile.loc[profile.ai_daily.idxmin()]
    n = int(profile.n.sum())
    spread = {m.label: (profile[m.key].max() - profile[m.key].min()) / profile[m.key].mean() for m in METRICS}
    flat = min(spread, key=spread.get)
    corr = profile.median_sal.corr(profile.ai_daily, method="spearman")
    note = Note(
        "f8_1", f"{top_ai[Col.ROLE]} dùng AI hằng ngày nhiều nhất ({fmt_pct(top_ai.ai_daily, 0)}), {top_sal[Col.ROLE]} có lương cao nhất",
        f"Trong {len(profile)} vai trò, tỷ lệ dùng AI hằng ngày từ {fmt_pct(low_ai.ai_daily, 0)} ({low_ai[Col.ROLE]}) đến {fmt_pct(top_ai.ai_daily, 0)} ({top_ai[Col.ROLE]}). "
        f"{top_sal[Col.ROLE]} có median lương cao nhất ({fmt_usd(top_sal.median_sal)}) và median kinh nghiệm {fmt_num(top_sal.median_exp, 0)} năm. "
        f"Chỉ số ít chênh lệch nhất giữa các vai trò là '{flat}' (khoảng cách cao nhất và thấp nhất bằng {fmt_pct(spread[flat] * 100, 0)} giá trị trung bình).",
        f"Hệ số tương quan hạng Spearman giữa median lương và tỷ lệ dùng AI hằng ngày qua {len(profile)} vai trò là {fmt_num(corr, 2)}: {describe_corr(corr)}.",
        sal_footer(n, f"{len(profile)} vai trò đủ {Cfg.min_role_n} dòng; mỗi trục chia cho giá trị cao nhất giữa {len(profile)} vai trò (đỉnh = 1), dải giá trị thật ghi cạnh tên trục."), n)
    theta = [axis_text(m, profile) for m in METRICS]
    fig = go.Figure()
    for color, name in zip(Pal.cat, picked):
        vals = unit.loc[name].tolist()
        fig.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=theta + theta[:1], name=name, fill="toself", opacity=0.55,
                                      line={"color": color, "width": SPIDER_LINE_WIDTH}, fillcolor=hex_alpha(color, SPIDER_FILL_ALPHA)))
    fig.update_layout(polar={"domain": {"y": [0.14, 0.86]}, "radialaxis": {"visible": True, "range": [0, 1], "tickvals": [0, 0.5, 1], "tickfont": {"size": 12}},
                             "angularaxis": {"tickfont": {"size": 16}}},
                      legend={"font": {"size": 18}, "x": 0.82, "y": 0.9})
    export_table(profile, "f8_1")
    return style_plotly(fig, note), note


def fig_f8_2(profile: pd.DataFrame, picked: list):
    """f8_2: biểu đồ chấm giá trị thật của 4 chỉ số cho mọi vai trò, 3 vai trò chọn được tô màu."""
    note = Note(
        "f8_2", "Giá trị thật của 4 chỉ số: vai trò tô màu là 3 vai trò trong spider",
        "Mỗi ô con là một chỉ số; mỗi chấm là một vai trò, sắp theo giá trị. " + "; ".join(
            f"{m.label}: cao nhất {profile.loc[profile[m.key].idxmax(), Col.ROLE]} ({fmt_num(profile[m.key].max(), m.digits)}{'' if m.unit == '%' else ' '}{m.unit})" for m in METRICS) + ".",
        "Dùng biểu đồ này khi cần đọc số chính xác, vì spider chỉ phù hợp để so sánh hình dạng tổng quát.",
        sal_footer(int(profile.n.sum()), f"{len(profile)} vai trò đủ {Cfg.min_role_n} dòng; chấm màu là 3 vai trò ở biểu đồ spider."), int(profile.n.sum()))
    fig, axes = new_fig(note, ncols=len(METRICS), left=0.17)
    fig.subplots_adjust(wspace=0.25)
    order = profile.sort_values("median_sal")[Col.ROLE].tolist()
    colors = {name: Pal.cat[i] for i, name in enumerate(picked)}
    for ax, metric in zip(axes, METRICS):
        values = profile.set_index(Col.ROLE).loc[order, metric.key]
        is_salary = metric.key == "median_sal"
        ax.scatter(values / (THOUSAND if is_salary else 1), range(len(order)), s=DOT_SIZE, color=[colors.get(r, Pal.neutral) for r in order], zorder=3)
        ax.set_title(f"{metric.label} ({'nghìn USD' if is_salary else metric.unit})" if "(" not in metric.label else metric.label, fontsize=7, loc="left")
        ax.set_yticks(range(len(order)), order if ax is axes[0] else [], fontsize=7)
        ax.tick_params(axis="x", labelsize=7)
        ax.locator_params(axis="x", nbins=4)
    export_table(profile, "f8_2")
    return fig, note


# %%
profile = role_profile(df_sal, roles)
picked_roles = pick_spider_roles(profile)
display(profile.round(1))
print("3 vai trò vẽ spider:", picked_roles)

# %%
finish(*fig_f8_1(profile, picked_roles))

# %%
finish(*fig_f8_2(profile, picked_roles))
