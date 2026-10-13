# %% [markdown]
# ## 3. Q2–Q4 – Xu hướng công nghệ
# Dữ liệu chỉ có năm 2025 nên không đo được thay đổi theo thời gian. Ta dùng ba chỉ số thay thế cho "xu hướng":
# **đang dùng** (`HaveWorkedWith`), **muốn dùng** (`WantToWorkWith`) và **được ngưỡng mộ** (`Admired`: trong những người đang dùng, tỷ lệ muốn tiếp tục dùng).
# Mẫu số mỗi chỉ số là số người có trả lời cột tương ứng. Với `Admired`, mẫu số là người đang dùng công nghệ đó và có trả lời mục "ngưỡng mộ"
# (khoảng 4.600 người đang dùng ngôn ngữ nhưng bỏ trống cả mục "muốn dùng", không đủ cơ sở để coi là "không ngưỡng mộ").

# %%
import itertools

import networkx as nx
import plotly.express as px
from networkx.algorithms import community


@dataclass(frozen=True)
class TechGroup:
    """Một nhóm công nghệ: tên hiển thị, cột dữ liệu và màu."""
    name: str
    col: str
    color: str


TECH_GROUPS = (
    TechGroup("Ngôn ngữ", Col.LANG_HAVE, Pal.cat[0]),
    TechGroup("CSDL", Col.DB_HAVE, Pal.cat[1]),
    TechGroup("Cloud và nền tảng", Col.PLAT_HAVE, Pal.cat[2]),
    TechGroup("Web framework", Col.WEB_HAVE, Pal.cat[3]),
)
TOP_BAR = 15
TOP_TREEMAP = 8
TOP_SANKEY = 7
TOP_DIVERGING = 8
EDGE_MIN_SHARE = 2.0
EDGE_MIN_LIFT = 1.5
SANKEY_MIN_SHARE = 45.0
NODE_SIZE_SCALE = 22.0
EDGE_WIDTH_SCALE = 1.2
SPRING_K = 2.0
SCATTER_LABELS = 14
LINK_ALPHA = 0.45
ROOT_KEY = "(?)"


def lang_table(df: pd.DataFrame) -> pd.DataFrame:
    """Bảng % đang dùng, % muốn dùng, % ngưỡng mộ cho từng ngôn ngữ."""
    have_pct, have_n = share_answered(df, Col.LANG_HAVE)
    want_pct, want_n = share_answered(df, Col.LANG_WANT)
    adm_rows = df[df[Col.LANG_ADM].notna()]
    users_adm = explode_multi(adm_rows, Col.LANG_HAVE)[Col.VALUE].value_counts()
    admired = explode_multi(adm_rows, Col.LANG_ADM)[Col.VALUE].value_counts()
    table = pd.DataFrame({"have_pct": have_pct, "want_pct": want_pct})
    table["admired_pct"] = admired / users_adm * 100
    table["users"] = (have_pct * have_n / 100).round().astype(int)
    table["want_gap"] = table.want_pct - table.have_pct
    result = table.dropna().sort_values("have_pct", ascending=False)
    result.attrs["n_have"] = have_n
    return result


lang = lang_table(df_all)


# %%
def fig_f2_1(df: pd.DataFrame):
    """f2_1: top ngôn ngữ đang được dùng nhiều nhất."""
    pct, n = share_answered(df, Col.LANG_HAVE)
    top = pct.head(TOP_BAR)[::-1]
    per_person = explode_multi(df, Col.LANG_HAVE).groupby(Col.ID).size().median()
    t3 = list(pct.index[:3])
    note = Note(
        "f2_1", f"{t3[0]}, {t3[1]} và {t3[2]} là ba ngôn ngữ được dùng nhiều nhất",
        f"{t3[0]} có {fmt_pct(pct.iloc[0])} người dùng, {t3[1]} {fmt_pct(pct.iloc[1])}, {t3[2]} {fmt_pct(pct.iloc[2])} (trên {fmt_int(n)} người có trả lời). "
        f"Một người dùng trung bình {fmt_num(per_person, 0)} ngôn ngữ, nên tổng tỷ lệ vượt 100%.",
        "Nhóm ngôn ngữ này có nhiều người dùng nhất trong mẫu, nên là điểm khởi đầu hợp lý cho người mới nếu muốn học cùng công cụ với số đông.",
        source_line(n, f"Người có trả lời mục ngôn ngữ đang dùng, {TOP_BAR} ngôn ngữ đầu."), n)
    fig, ax = new_fig(note, left=0.20)
    ax.barh(top.index, top.to_numpy(), color=[Pal.accent if i >= len(top) - 3 else Pal.neutral for i in range(len(top))], height=BAR_HEIGHT)
    annotate_bars_h(ax, top.to_numpy(), [fmt_pct(v) for v in top])
    ax.set_xlabel("Tỷ lệ người dùng (%)")
    ax.set_xlim(0, top.max() * 1.12)
    export_table(pct.rename("pct").reset_index(), "f2_1")
    return fig, note


def group_counts(df: pd.DataFrame, group: TechGroup) -> pd.DataFrame:
    """Số người dùng từng công nghệ của một nhóm."""
    counts = explode_multi(df, group.col)[Col.VALUE].value_counts().head(TOP_TREEMAP)
    return pd.DataFrame({"group": group.name, "tech": counts.index, "users": counts.to_numpy()})


def fig_f2_2(df: pd.DataFrame):
    """f2_2: treemap hệ sinh thái công nghệ theo nhóm."""
    table = pd.concat([group_counts(df, g) for g in TECH_GROUPS], ignore_index=True)
    leaders = table.groupby("group", sort=False).first()["tech"]
    n = int(df[[g.col for g in TECH_GROUPS]].notna().any(axis=1).sum())
    note = Note(
        "f2_2", f"{leaders.iloc[0]}, {leaders.iloc[1]}, {leaders.iloc[2]} và {leaders.iloc[3]} dẫn đầu từng nhóm công nghệ",
        f"Treemap gồm {len(table)} công nghệ (top {TOP_TREEMAP} mỗi nhóm); diện tích tỷ lệ với số người dùng. "
        f"Người dùng ngôn ngữ lớn nhất ({leaders.iloc[0]}) là {fmt_int(table.users.max())} người.",
        "Mỗi nhóm có một vài công nghệ đứng đầu về số người dùng; người mới có thể ưu tiên các công nghệ này vì có nhiều người dùng nhất trong mẫu.",
        source_line(n, f"Người có trả lời ít nhất một nhóm công nghệ; top {TOP_TREEMAP} mỗi nhóm; diện tích tính theo số người dùng, không so trực tiếp giữa các nhóm."), n)
    colors = {g.name: g.color for g in TECH_GROUPS} | {ROOT_KEY: "#FFFFFF"}
    fig = px.treemap(table, path=[px.Constant("Công nghệ"), "group", "tech"], values="users", color="group", color_discrete_map=colors)
    fig.update_traces(texttemplate="%{label}<br>%{value:,.0f}", textfont={"size": 20}, marker_line_width=2)
    export_table(table, "f2_2")
    return style_plotly(fig, note), note


def fig_f2_3(df: pd.DataFrame):
    """f2_3: top công nghệ trong CSDL, nền tảng và web framework (tỷ lệ %)."""
    groups = TECH_GROUPS[1:]
    results = [share_answered(df, g.col) for g in groups]
    leaders = [pct.index[0] for pct, _ in results]
    tops = [pct.iloc[0] for pct, _ in results]
    note = Note(
        "f2_3", f"{leaders[0]}, {leaders[1]} và {leaders[2]} dẫn đầu CSDL, cloud và web framework",
        "; ".join(f"{g.name}: {pct.index[0]} {fmt_pct(pct.iloc[0])} (n = {fmt_int(n)})" for g, (pct, n) in zip(groups, results)) + ".",
        f"Công nghệ đứng đầu mỗi nhóm có tỷ lệ dùng từ {fmt_pct(min(tops), 0)} đến {fmt_pct(max(tops), 0)}; vì người trả lời chọn nhiều đáp án, đây là tỷ lệ người dùng chứ không phải thị phần.",
        source_line(sum(n for _, n in results), f"Top {TOP_TREEMAP} mỗi nhóm; mẫu số là số người trả lời từng nhóm (n cộng của 3 nhóm)."),
        sum(n for _, n in results))
    fig, axes = new_fig(note, ncols=3, left=0.12, sharex=False)
    fig.subplots_adjust(wspace=0.95)
    for ax, group, (pct, _) in zip(axes, groups, results):
        top = pct.head(TOP_TREEMAP)[::-1]
        ax.barh(top.index, top.to_numpy(), color=group.color, height=BAR_HEIGHT)
        ax.set_title(group.name, fontsize=9, loc="left")
        ax.tick_params(axis="y", labelsize=7)
        annotate_bars_h(ax, top.to_numpy(), [fmt_pct(v, 0) for v in top])
        ax.set_xlim(0, top.max() * 1.25)
    export_table(pd.concat([pct.head(TOP_TREEMAP).rename("pct").reset_index().assign(group=g.name) for g, (pct, _) in zip(groups, results)]), "f2_3")
    return fig, note


# %%
finish(*fig_f2_1(df_all))

# %%
finish(*fig_f2_2(df_all))

# %%
finish(*fig_f2_3(df_all))


# %% [markdown]
# ### Q3 – Dùng nhiều có được ngưỡng mộ nhiều không?
# Mỗi điểm là một ngôn ngữ. Trục ngang: % người dùng. Trục dọc: % ngưỡng mộ (tỷ lệ người đang dùng muốn tiếp tục dùng).

# %%
def fig_f3_1(table: pd.DataFrame):
    """f3_1: quan hệ giữa mức dùng và mức ngưỡng mộ của từng ngôn ngữ."""
    most_adm, most_used = table.admired_pct.idxmax(), table.have_pct.idxmax()
    corr = table.have_pct.corr(table.admired_pct, method="spearman")
    note = Note(
        "f3_1", f"{most_used} dùng nhiều nhất nhưng chỉ {fmt_pct(table.admired_pct[most_used], 0)} ngưỡng mộ; {most_adm} đạt {fmt_pct(table.admired_pct.max(), 0)}",
        f"Trong {len(table)} ngôn ngữ, hệ số tương quan hạng Spearman giữa mức dùng và mức ngưỡng mộ là {fmt_num(corr, 2)}. "
        f"{most_adm} được ngưỡng mộ nhất ({fmt_pct(table.admired_pct.max())}), trong khi ngưỡng mộ thấp nhất là {table.admired_pct.idxmin()} ({fmt_pct(table.admired_pct.min())}).",
        "Mức dùng cao không đảm bảo ngưỡng mộ cao; chọn ngôn ngữ nên cân nhắc cả mức phổ biến (dùng nhiều) lẫn mức hài lòng của người đang dùng (ngưỡng mộ).",
        source_line(table.attrs["n_have"], "Mỗi điểm là một ngôn ngữ; ngưỡng mộ tính trên người đang dùng ngôn ngữ đó và có trả lời mục ngưỡng mộ; đường nét đứt là median."),
        table.attrs["n_have"])
    fig, ax = new_fig(note, left=0.08)
    ax.scatter(table.have_pct, table.admired_pct, s=40, color=Pal.accent, alpha=0.85)
    labelled = set(table.nlargest(SCATTER_LABELS // 2, "have_pct").index) | set(table.nlargest(SCATTER_LABELS // 2, "admired_pct").index)
    for name in labelled:
        ax.annotate(name, (table.have_pct[name], table.admired_pct[name]), xytext=(4, 3), textcoords="offset points", fontsize=7)
    ax.axhline(table.admired_pct.median(), color=Pal.neutral, linestyle="--", linewidth=0.8)
    ax.axvline(table.have_pct.median(), color=Pal.neutral, linestyle="--", linewidth=0.8)
    ax.set_xlabel("Tỷ lệ người đang dùng (%)")
    ax.set_ylabel("Tỷ lệ ngưỡng mộ (%)")
    ax.set_xlim(right=table.have_pct.max() * 1.15)
    export_table(table.reset_index().rename(columns={"index": "lang"}), "f3_1")
    return fig, note


def fig_f3_2(table: pd.DataFrame):
    """f3_2: chênh lệch giữa mức muốn dùng và mức đang dùng."""
    gap = table.want_gap.sort_values()
    picked = pd.concat([gap.head(TOP_DIVERGING), gap.tail(TOP_DIVERGING)])
    up, down = gap.index[-1], gap.index[0]
    note = Note(
        "f3_2", f"{up} được muốn dùng vượt mức đang dùng {fmt_num(gap.iloc[-1])} điểm %, {down} thấp hơn {fmt_num(abs(gap.iloc[0]))} điểm %",
        f"Ngôn ngữ có mức muốn dùng cao hơn mức đang dùng nhiều nhất: {', '.join(gap.index[::-1][:3])}. "
        f"Ngôn ngữ mà mức muốn dùng thấp hơn mức đang dùng nhiều nhất: {', '.join(gap.index[:3])}.",
        "Đây là chỉ số thay thế cho xu hướng: ngôn ngữ có chênh lệch dương lớn đang được người dùng kỳ vọng nhiều hơn so với mức dùng hiện tại.",
        source_line(table.attrs["n_have"], f"Chênh lệch = % muốn dùng trừ % đang dùng (điểm phần trăm); {TOP_DIVERGING} ngôn ngữ cao nhất và thấp nhất."),
        table.attrs["n_have"])
    fig, ax = new_fig(note, left=0.18)
    ax.barh(picked.index, picked.to_numpy(), color=[Pal.accent if v > 0 else Pal.accent2 for v in picked], height=BAR_HEIGHT)
    for idx, val in enumerate(picked):
        ax.text(val + (0.3 if val > 0 else -0.3), idx, fmt_num(val), va="center", ha="left" if val > 0 else "right", fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Muốn dùng trừ đang dùng (điểm %)")
    ax.margins(x=0.1)
    export_table(gap.rename("want_gap").reset_index(), "f3_2")
    return fig, note


# %%
finish(*fig_f3_1(lang))

# %%
finish(*fig_f3_2(lang))


# %% [markdown]
# ### Q4 – Ngôn ngữ nào đi cùng nhau, và người dùng X muốn dùng Y nào?
# Mạng chỉ giữ các cặp ngôn ngữ vừa đủ phổ biến (cùng xuất hiện ở ít nhất 2% người trả lời) vừa đi cùng nhau nhiều hơn mức ngẫu nhiên (lift ≥ 1,5) để tránh "búi tóc". Vị trí nút chỉ để quan sát, không mang ý nghĩa đo lường.
# Sankey cho thấy người đang dùng X cũng muốn dùng Y (đây là mong muốn tại một thời điểm, không phải chuyển đổi thực tế).

# %%
def cooccurrence(df: pd.DataFrame):
    """Ma trận số người dùng chung từng cặp ngôn ngữ."""
    flags = pd.crosstab(*[explode_multi(df, Col.LANG_HAVE)[c] for c in (Col.ID, Col.VALUE)]).clip(upper=1)
    return flags.T.dot(flags), len(flags)


def build_graph(df: pd.DataFrame):
    """Dựng đồ thị đồng xuất hiện: giữ cặp đủ phổ biến và đi cùng nhau hơn mức ngẫu nhiên (lift)."""
    matrix, n = cooccurrence(df)
    usage = {name: matrix.loc[name, name] / n * 100 for name in matrix.index}
    graph = nx.Graph()
    for a, b in itertools.combinations(matrix.index, 2):
        share = matrix.loc[a, b] / n * 100
        lift = share / (usage[a] * usage[b] / 100)
        if share >= EDGE_MIN_SHARE and lift >= EDGE_MIN_LIFT:
            graph.add_edge(a, b, weight=lift, share=share)
    return graph, {name: usage[name] for name in graph.nodes}, n


def fig_f4_1(df: pd.DataFrame):
    """f4_1: mạng các ngôn ngữ thường được dùng chung."""
    graph, usage, n = build_graph(df)
    groups = list(community.greedy_modularity_communities(graph, weight="weight"))
    hub = max(graph.degree, key=lambda item: item[1])
    top_edge = max(graph.edges(data="weight"), key=lambda item: item[2])
    note = Note(
        "f4_1", f"Có {len(groups)} cụm ngôn ngữ hay được dùng chung",
        f"Đồ thị có {graph.number_of_nodes()} ngôn ngữ và {graph.number_of_edges()} cặp. Một cặp được giữ khi cùng xuất hiện ở ít nhất {fmt_num(EDGE_MIN_SHARE, 0)}% người trả lời "
        f"và có lift ≥ {fmt_num(EDGE_MIN_LIFT)} (đi cùng nhau nhiều gấp {fmt_num(EDGE_MIN_LIFT)} lần so với ngẫu nhiên). "
        f"Cặp gắn bó nhất là {top_edge[0]} và {top_edge[1]} (lift {fmt_num(top_edge[2])}); {hub[0]} nối với nhiều ngôn ngữ nhất ({hub[1]} cạnh).",
        "Số cạnh nhiều của một nút chỉ cho biết ngôn ngữ hay đi cùng ngôn ngữ khác, không có nghĩa là quan trọng hơn; một số cụm gợi ý các ngôn ngữ có thể học cùng nhau.",
        source_line(n, f"Người có trả lời ngôn ngữ đang dùng; cạnh = cặp cùng xuất hiện ≥{fmt_num(EDGE_MIN_SHARE, 0)}% người và lift ≥{fmt_num(EDGE_MIN_LIFT)}; nút to = nhiều người dùng; màu = cụm."), n)
    pos = nx.spring_layout(graph, seed=Cfg.seed, k=SPRING_K / np.sqrt(graph.number_of_nodes()), weight="weight")
    fig, ax = new_fig(note, left=0.02)
    ax.axis("off")
    node_color = {name: Pal.cat[i % len(Pal.cat)] for i, grp in enumerate(groups) for name in grp}
    widths = [graph[a][b]["weight"] * EDGE_WIDTH_SCALE for a, b in graph.edges]
    nx.draw_networkx_edges(graph, pos, ax=ax, width=widths, edge_color=Pal.neutral, alpha=0.6)
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_size=[usage[v] * NODE_SIZE_SCALE for v in graph.nodes],
                           node_color=[node_color[v] for v in graph.nodes], alpha=0.9)
    nx.draw_networkx_labels(graph, pos, ax=ax, font_size=7, font_weight="bold")
    export_table(nx.to_pandas_edgelist(graph), "f4_1")
    return fig, note


def flow_matrix(df: pd.DataFrame, names: list) -> tuple:
    """Số người đang dùng X (hàng) và muốn dùng Y (cột), loại đường chéo."""
    both = df[df[Col.LANG_HAVE].notna() & df[Col.LANG_WANT].notna()]
    have = pd.crosstab(*[explode_multi(both, Col.LANG_HAVE)[c] for c in (Col.ID, Col.VALUE)])[names]
    want = pd.crosstab(*[explode_multi(both, Col.LANG_WANT)[c] for c in (Col.ID, Col.VALUE)])[names]
    flows = have.T.dot(want.reindex(have.index).fillna(0))
    return flows, have.sum(), len(both)


def fig_f4_2(df: pd.DataFrame):
    """f4_2: Sankey từ ngôn ngữ đang dùng sang ngôn ngữ muốn dùng, chỉ giữ luồng mạnh."""
    names = list(share_answered(df, Col.LANG_HAVE)[0].index[:TOP_SANKEY])
    flows, users, n = flow_matrix(df, names)
    cross = flows.mask(np.eye(len(flows), dtype=bool), 0)
    share = cross.div(users, axis=0) * 100
    count = len(names)
    strong = [(i, j) for i in range(count) for j in range(count) if share.iloc[i, j] >= SANKEY_MIN_SHARE]
    col_mean = share.where(~np.eye(count, dtype=bool)).mean()
    ranked = sorted(strong, key=lambda pair: share.iloc[pair], reverse=True)
    src, dst = ranked[0]
    top_flows = "; ".join(f"{names[i]} → {names[j]} ({fmt_pct(share.iloc[i, j], 0)})" for i, j in ranked[:3])
    note = Note(
        "f4_2", f"Người dùng {names[src]} thường muốn dùng thêm {names[dst]} ({fmt_pct(share.iloc[src, dst], 0)})",
        f"Có {len(strong)} luồng mạnh, tức ít nhất {fmt_num(SANKEY_MIN_SHARE, 0)}% người đang dùng X muốn dùng Y, trong {TOP_SANKEY} ngôn ngữ phổ biến nhất. "
        f"Luồng mạnh nhất: {fmt_pct(share.iloc[src, dst])} người đang dùng {names[src]} muốn dùng {names[dst]}. "
        f"Ba luồng mạnh nhất: {top_flows}.",
        f"Đây là mong muốn tại một thời điểm, không phải số người thực sự chuyển đổi. Tỷ lệ muốn dùng trung bình qua các nhóm nguồn khác nhau theo ngôn ngữ đích: {fmt_pct(col_mean.max(), 0)} với {names[int(col_mean.argmax())]} và {fmt_pct(col_mean.min(), 0)} với {names[int(col_mean.argmin())]}.",
        source_line(n, f"Người có trả lời cả hai mục; {TOP_SANKEY} ngôn ngữ phổ biến nhất; chỉ vẽ luồng ≥{fmt_num(SANKEY_MIN_SHARE, 0)}% người dùng X muốn dùng Y, bỏ luồng cùng ngôn ngữ."), n)
    labels = [f"Đang dùng: {v}" for v in names] + [f"Muốn dùng: {v}" for v in names]
    colors = list(Pal.cat[:count]) * 2
    fig = go.Figure(go.Sankey(
        node={"label": labels, "color": colors, "pad": 22, "thickness": 20},
        link={"source": [i for i, _ in strong], "target": [count + j for _, j in strong],
              "value": [float(cross.iloc[i, j]) for i, j in strong],
              "color": [hex_alpha(Pal.cat[i], LINK_ALPHA) for i, _ in strong]}))
    fig.update_traces(textfont={"size": 16})
    export_table(share.reset_index().rename(columns={Col.VALUE: "dang_dung"}), "f4_2")
    return style_plotly(fig, note), note


def hex_alpha(color: str, alpha: float) -> str:
    """Đổi mã màu hex sang rgba có độ trong suốt."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{alpha})"


# %%
finish(*fig_f4_1(df_all))

# %%
finish(*fig_f4_2(df_all))
