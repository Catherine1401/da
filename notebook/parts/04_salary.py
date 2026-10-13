# %% [markdown]
# ## 4. Q5–Q7 – Mức lương
# Lương là `ConvertedCompYearly` (USD danh nghĩa, đã quy đổi sẵn trong dữ liệu gốc, chưa điều chỉnh sức mua), tính trên bảng `df_sal`
# (lập trình viên chuyên nghiệp, lương 1.000–500.000 USD). Vì lương lệch phải mạnh nên ta dùng **median**, kèm khoảng tin cậy bootstrap 95%.
# Ghi chú: số liệu là tự khai báo và mẫu lệch về Mỹ, Đức, Ấn Độ nên chỉ nên đọc như mô tả mẫu khảo sát, không phải thị trường lao động nói chung.

# %%
import joypy
import plotly.express as px

N_BINS = 40
LOG_TICKS = (10_000, 30_000, 100_000, 300_000)
TOP_RANK = 10
BOTTOM_RANK = 10
HEAT_LANGS = 10
HEAT_ROLES = 6
RIDGE_OVERLAP = 1.2
RIDGE_LINEWIDTH = 0.8
RIDGE_RANGE = (3.0, 5.7)
HEAT_BOTTOM = 0.24
RIDGE_ALPHA = 0.85
MAP_COLORSCALE = "Blues"
MAP_CENTER_LON = 10
MAP_LAT_RANGE = (-58, 85)


def fmt_usd(value) -> str:
    """Định dạng tiền USD kiểu Việt Nam."""
    return f"{fmt_int(value)} USD"


def sal_footer(n: int, extra: str = "") -> str:
    """Chú thích chân chuẩn cho biểu đồ lương."""
    return source_line(n, f"Lập trình viên chuyên nghiệp, lương {fmt_int(Cfg.sal_min)}–{fmt_int(Cfg.sal_max)} USD (USD danh nghĩa). {extra}".strip())


# %%
def fig_f5_1(df: pd.DataFrame):
    """f5_1: phân phối lương toàn mẫu trên thang log, median và mean."""
    sal = df[Col.SAL]
    med, mean = sal.median(), sal.mean()
    q1, q3 = sal.quantile(0.25), sal.quantile(0.75)
    note = Note(
        "f5_1", f"Median lương {fmt_usd(med)} thấp hơn mean {fmt_usd(mean)}: phân phối lệch phải",
        f"Một nửa số người có lương dưới {fmt_usd(med)}; 25% thấp nhất dưới {fmt_usd(q1)} và 25% cao nhất trên {fmt_usd(q3)}. "
        f"Mean cao hơn median {fmt_pct((mean / med - 1) * 100, 0)} vì một số ít người có lương rất cao kéo trung bình lên.",
        "Vì lương lệch phải, khi nói 'lương điển hình' phải dùng median thay vì mean để tránh kỳ vọng quá cao.",
        sal_footer(len(sal), "Trục ngang là thang log."), len(sal))
    fig, ax = new_fig(note, left=0.08)
    ax.hist(sal, bins=np.logspace(np.log10(Cfg.sal_min), np.log10(Cfg.sal_max), N_BINS), color=Pal.neutral, edgecolor="white")
    ax.set_xscale("log")
    for value, color, name in ((med, Pal.accent2, "Median"), (mean, Pal.accent, "Mean")):
        ax.axvline(value, color=color, linewidth=1.8)
        ax.text(value, ax.get_ylim()[1] * (0.95 if name == "Median" else 0.85), f" {name} {fmt_int(value)}", color=color, fontsize=8, fontweight="bold")
    ax.set_xticks(LOG_TICKS, [fmt_int(t) for t in LOG_TICKS])
    ax.set_xlabel("Lương năm (USD, thang log)")
    ax.set_ylabel("Số người")
    thousands_axis(ax, "y")
    export_table(pd.DataFrame({"stat": ["median", "mean", "q1", "q3"], "usd": [med, mean, q1, q3]}), "f5_1")
    return fig, note


def fig_f5_2(df: pd.DataFrame, role_names: list):
    """f5_2: ridgeline phân phối lương theo vai trò, sắp theo median."""
    data = df[df[Col.ROLE].isin(role_names)].copy()
    table = median_table(data, Col.ROLE, with_ci=False).sort_values("median", ascending=False)
    order = table[Col.ROLE].tolist()
    data["log_sal"] = np.log10(data[Col.SAL])
    data[Col.ROLE] = pd.Categorical(data[Col.ROLE], categories=order, ordered=True)
    hi, lo = table.iloc[0], table.iloc[-1]
    iqr = data.groupby(Col.ROLE, observed=True)[Col.SAL].apply(lambda v: v.quantile(0.75) - v.quantile(0.25)).median()
    spread = hi["median"] - lo["median"]
    overlap = (f"Khoảng tứ phân vị điển hình trong một vai trò ({fmt_usd(iqr)}) lớn hơn chênh lệch giữa median cao nhất và thấp nhất ({fmt_usd(spread)}), "
               "nên chênh lệch trong cùng vai trò lớn hơn giữa các vai trò." if iqr > spread else
               f"Khoảng tứ phân vị điển hình trong một vai trò ({fmt_usd(iqr)}) nhỏ hơn chênh lệch giữa median cao nhất và thấp nhất ({fmt_usd(spread)}), nên vai trò phân biệt lương khá rõ.")
    note = Note(
        "f5_2", f"{hi[Col.ROLE]} có median lương cao nhất ({fmt_usd(hi['median'])}), gấp {fmt_num(hi['median'] / lo['median'])} lần {lo[Col.ROLE]}",
        f"Trong {len(order)} vai trò, median thấp nhất là {lo[Col.ROLE]} ({fmt_usd(lo['median'])}) và cao nhất là {hi[Col.ROLE]} ({fmt_usd(hi['median'])}). " + overlap,
        "Vai trò gắn với mức lương điển hình, nhưng người trong cùng một vai trò vẫn có lương khác nhau; cần xét thêm nước và kinh nghiệm.",
        sal_footer(len(data), f"{len(order)} vai trò có ít nhất {Cfg.min_role_n} dòng; vạch đứng là median; trục ngang là log10 của lương."), len(data))
    fig, axes = joypy.joyplot(data, by=Col.ROLE, column="log_sal", figsize=(Cfg.fig_w, Cfg.fig_h), color=Pal.accent, alpha=RIDGE_ALPHA,
                              overlap=RIDGE_OVERLAP, linewidth=RIDGE_LINEWIDTH, ylabelsize=7, xlabelsize=8, grid="y", x_range=RIDGE_RANGE)
    for ax, key in zip(axes[:-1], order):
        ax.axvline(np.log10(table.set_index(Col.ROLE).loc[key, "median"]), color=Pal.accent2, linewidth=1.2)
    axes[-1].set_xticks([np.log10(t) for t in LOG_TICKS], [fmt_int(t) for t in LOG_TICKS])
    axes[-1].set_xlabel("Lương năm (USD, thang log)")
    decorate_fig(fig, note, left=0.17)
    export_table(table, "f5_2")
    return fig, note


def fig_f5_3(df: pd.DataFrame):
    """f5_3: median lương theo nhóm năm kinh nghiệm làm việc."""
    data = df.dropna(subset=[Col.EXPBIN])
    table = median_table(data, Col.EXPBIN)
    medians = table["median"].to_numpy()
    rising = bool(np.all(np.diff(medians) > 0))
    first, last = table.iloc[0], table.iloc[-1]
    peak = table.loc[table["median"].idxmax()]
    overall = df[Col.SAL].median()
    title = (f"Median lương tăng từ {fmt_usd(first['median'])} (0–2 năm) lên {fmt_usd(last['median'])} (21+ năm)" if rising
             else f"Median lương cao nhất ở nhóm {peak[Col.EXPBIN]} năm kinh nghiệm ({fmt_usd(peak['median'])})")
    note = Note(
        "f5_3", title,
        f"Median lương của nhóm 21+ năm gấp {fmt_num(last['median'] / first['median'])} lần nhóm 0–2 năm. "
        f"{'Median tăng đều qua mọi nhóm kinh nghiệm' if rising else 'Median không tăng đều qua mọi nhóm kinh nghiệm'}; "
        f"nhóm 3–5 năm có median {fmt_usd(table.iloc[1]['median'])}.",
        f"Nhóm 0–2 năm có median bằng {fmt_pct(first['median'] / overall * 100, 0)} median toàn mẫu ({fmt_usd(overall)}); người mới nên đặt kỳ vọng tương ứng.",
        sal_footer(int(table.n.sum()), "Vùng tô là khoảng tin cậy bootstrap 95% của median; số dưới điểm là cỡ mẫu từng nhóm."), int(table.n.sum()))
    fig, ax = new_fig(note, left=0.10)
    x = np.arange(len(table))
    ax.fill_between(x, table.lo, table.hi, color=Pal.accent, alpha=0.2)
    ax.plot(x, table["median"], color=Pal.accent, marker="o", linewidth=2)
    for xi, row in zip(x, table.itertuples()):
        ax.text(xi, row.median, f"{fmt_int(row.median)}", ha="center", va="bottom", fontsize=8, fontweight="bold")
        ax.text(xi, ax.get_ylim()[0], f"n={fmt_int(row.n)}", ha="center", va="bottom", fontsize=7, color="#555555")
    ax.set_xticks(x, table[Col.EXPBIN].astype(str))
    ax.set_xlabel("Số năm kinh nghiệm làm việc (WorkExp)")
    ax.set_ylabel("Median lương (USD)")
    thousands_axis(ax, "y")
    export_table(table, "f5_3")
    return fig, note


# %%
finish(*fig_f5_1(df_sal))

# %%
finish(*fig_f5_2(df_sal, roles))

# %%
finish(*fig_f5_3(df_sal))


# %% [markdown]
# ### Q6 – Công nghệ nào đi cùng mức lương cao?
# Cẩn thận: so sánh trực tiếp lương theo ngôn ngữ có thể gây hiểu nhầm vì ngôn ngữ phổ biến ở nước lương cao trông "lương cao" chỉ do người dùng ở đó.
# Hai biểu đồ này là mô tả; phần hồi quy ở mục 7 sẽ tách ảnh hưởng của quốc gia và kinh nghiệm.

# %%
def lang_salary(df: pd.DataFrame) -> pd.DataFrame:
    """Bảng lương dạng dài theo từng ngôn ngữ đang dùng."""
    longer = explode_multi(df, Col.LANG_HAVE).merge(df[[Col.ID, Col.SAL, Col.ROLE]], on=Col.ID)
    return longer.rename(columns={Col.VALUE: "lang"})


def fig_f6_1(df: pd.DataFrame):
    """f6_1: median lương theo ngôn ngữ phổ biến (chưa tách ảnh hưởng quốc gia)."""
    longer = lang_salary(df)
    top = longer["lang"].value_counts().head(Cfg.top_lang).index
    table = median_table(longer[longer["lang"].isin(top)], "lang").sort_values("median")
    hi, lo = table.iloc[-1], table.iloc[0]
    overall = df[Col.SAL].median()
    pairs = [(a, b) for i, a in table.reset_index(drop=True).iterrows() for j, b in table.reset_index(drop=True).iterrows() if i < j]
    overlap = np.mean([max(a.lo, b.lo) <= min(a.hi, b.hi) for a, b in pairs])
    note = Note(
        "f6_1", f"Giữa {Cfg.top_lang} ngôn ngữ phổ biến, median lương chênh {fmt_pct((hi['median'] / lo['median'] - 1) * 100, 0)}: từ {lo['lang']} đến {hi['lang']}",
        f"{hi['lang']} có median {fmt_usd(hi['median'])} (n = {fmt_int(hi['n'])}), {lo['lang']} có {fmt_usd(lo['median'])} (n = {fmt_int(lo['n'])}); median toàn mẫu là {fmt_usd(overall)}. "
        f"Khoảng tin cậy 95% của {fmt_pct(overlap * 100, 0)} số cặp ngôn ngữ chồng lấn nhau, nên các chênh lệch này kém chắc chắn.",
        "Chưa thể kết luận ngôn ngữ nào 'trả lương cao hơn': khác biệt này có thể phản ánh cơ cấu nước và kinh nghiệm của người dùng (xem hồi quy).",
        sal_footer(int(longer[longer['lang'].isin(top)][Col.ID].nunique()), f"Mỗi người được tính ở mọi ngôn ngữ họ dùng; thanh sai số là khoảng tin cậy 95%; đường nét đứt là median toàn mẫu."),
        int(longer[longer['lang'].isin(top)][Col.ID].nunique()))
    fig, ax = new_fig(note, left=0.17)
    err = np.vstack([table["median"] - table.lo, table.hi - table["median"]])
    ax.barh(table["lang"], table["median"], xerr=err, color=Pal.accent, height=BAR_HEIGHT, error_kw={"ecolor": "#333333", "capsize": 2})
    ax.axvline(overall, color=Pal.accent2, linestyle="--", linewidth=1)
    ax.text(overall, -0.9, f" Median toàn mẫu {fmt_int(overall)}", color=Pal.accent2, fontsize=7)
    ax.set_xlabel("Median lương (USD)")
    thousands_axis(ax)
    export_table(table, "f6_1")
    return fig, note


def fig_f6_2(df: pd.DataFrame):
    """f6_2: heatmap median lương theo ngôn ngữ và vai trò, ô đủ cỡ mẫu mới tô màu."""
    longer = lang_salary(df)
    langs = longer["lang"].value_counts().head(HEAT_LANGS).index.tolist()
    role_names = longer[Col.ROLE].value_counts().head(HEAT_ROLES).index.tolist()
    sub = longer[longer["lang"].isin(langs) & longer[Col.ROLE].isin(role_names)]
    med = sub.pivot_table(index="lang", columns=Col.ROLE, values=Col.SAL, aggfunc="median").reindex(index=langs, columns=role_names)
    size = sub.pivot_table(index="lang", columns=Col.ROLE, values=Col.SAL, aggfunc="size").reindex(index=langs, columns=role_names)
    med = med.where(size >= Cfg.min_cell_n)
    best = med.idxmax(axis=1).value_counts()
    by_role = (med.max(axis=1) - med.min(axis=1)).mean()
    by_lang = (med.max(axis=0) - med.min(axis=0)).mean()
    which = (f"Khoảng cách median lớn nhất–nhỏ nhất trong một ngôn ngữ (qua {len(role_names)} vai trò) trung bình {fmt_usd(by_role)}, còn trong một vai trò (qua {len(langs)} ngôn ngữ) trung bình {fmt_usd(by_lang)}"
             + (": vai trò đi cùng chênh lệch lương lớn hơn ngôn ngữ (số nhóm so sánh khác nhau nên chỉ mang tính tham khảo)." if by_role > by_lang else ": ngôn ngữ đi cùng chênh lệch lương lớn hơn vai trò (số nhóm so sánh khác nhau nên chỉ mang tính tham khảo)."))
    note = Note(
        "f6_2", f"{best.index[0]} có median lương cao nhất ở {int(best.iloc[0])}/{len(langs)} ngôn ngữ được so sánh",
        f"Heatmap gồm {len(langs)} ngôn ngữ và {len(role_names)} vai trò phổ biến nhất ({med.notna().sum().sum()}/{med.size} ô đủ {Cfg.min_cell_n} người). "
        f"Giá trị cao nhất là {fmt_usd(np.nanmax(med.to_numpy()))}, thấp nhất là {fmt_usd(np.nanmin(med.to_numpy()))}.",
        which,
        sal_footer(int(sub[Col.ID].nunique()), f"Mỗi người được tính ở mọi ngôn ngữ họ dùng; ô dấu – là chưa đủ {Cfg.min_cell_n} người; số trong ô là median (nghìn USD)."), int(sub[Col.ID].nunique()))
    fig, ax = new_fig(note, left=0.14)
    fig.subplots_adjust(bottom=HEAT_BOTTOM)
    image = ax.imshow(med.to_numpy() / 1000, cmap=MAP_COLORSCALE, aspect="auto")
    ax.set_xticks(range(len(role_names)), role_names, rotation=20, ha="right", fontsize=7)
    ax.set_yticks(range(len(langs)), langs, fontsize=7)
    ax.grid(False)
    for i in range(len(langs)):
        for j in range(len(role_names)):
            value = med.iloc[i, j]
            ax.text(j, i, "–" if np.isnan(value) else fmt_num(value / 1000, 0), ha="center", va="center", fontsize=7,
                    color="white" if (not np.isnan(value) and value / 1000 > np.nanmax(med.to_numpy()) / 1000 * 0.6) else "#222222")
    fig.colorbar(image, ax=ax, label="Median lương (nghìn USD)", fraction=0.04)
    export_table(med.reset_index(), "f6_2")
    return fig, note


# %%
finish(*fig_f6_1(df_sal))

# %%
finish(*fig_f6_2(df_sal))


# %% [markdown]
# ### Q7 – Lương khác nhau thế nào giữa các nước, Việt Nam đứng đâu?
# Bản đồ chỉ tô màu **median lương** (đã chuẩn hóa theo từng nước, không phải số tuyệt đối), chỉ cho các nước đủ 30 dòng lương.
# Lưu ý: lương là USD danh nghĩa, chưa điều chỉnh sức mua; Việt Nam chỉ có 31 dòng nên kết quả mang tính tham khảo.

# %%
def country_table(df: pd.DataFrame, names: list) -> pd.DataFrame:
    """Bảng median lương và khoảng tin cậy theo nước, kèm mã ISO-3."""
    table = median_table(df[df[Col.COUNTRY].isin(names)], Col.COUNTRY)
    iso = df.drop_duplicates(Col.COUNTRY).set_index(Col.COUNTRY)[Col.ISO3]
    table[Col.ISO3] = table[Col.COUNTRY].map(iso)
    table["name"] = table[Col.COUNTRY].map(short_country)
    return table.sort_values("median", ascending=False).reset_index(drop=True)


def fig_f7_1(table: pd.DataFrame):
    """f7_1: choropleth median lương theo nước, Việt Nam đánh dấu."""
    vn = table[table[Col.COUNTRY] == VIETNAM].iloc[0]
    hi, lo = table.iloc[0], table.iloc[-1]
    note = Note(
        "f7_1", f"Median lương cao nhất ở {hi['name']} ({fmt_usd(hi['median'])}), thấp nhất ở {lo['name']} ({fmt_usd(lo['median'])}); Việt Nam {fmt_usd(vn['median'])}",
        f"Bản đồ có {len(table)} nước đủ {Cfg.min_country_n} dòng lương. Chênh lệch giữa nước cao nhất và thấp nhất là {fmt_num(hi['median'] / lo['median'])} lần. "
        f"Việt Nam có median {fmt_usd(vn['median'])} (khoảng tin cậy {fmt_int(vn['lo'])}–{fmt_int(vn['hi'])}, n = {int(vn['n'])}).",
        "Quốc gia là yếu tố gắn với khác biệt lương lớn nhất; số liệu Việt Nam chỉ tham khảo vì mẫu nhỏ và lương là USD danh nghĩa.",
        sal_footer(int(table.n.sum()), f"Chỉ nước đủ {Cfg.min_country_n} dòng lương; chấm cam là Việt Nam."), int(table.n.sum()))
    mapped = table.dropna(subset=[Col.ISO3])
    fig = px.choropleth(mapped, locations=Col.ISO3, color="median", hover_name="name", color_continuous_scale=MAP_COLORSCALE,
                        labels={"median": "Median lương (USD)"})
    fig.add_trace(go.Scattergeo(locations=["VNM"], locationmode="ISO-3", mode="markers+text", text=["Việt Nam"], textposition="bottom center",
                                marker={"size": 11, "color": Pal.accent2}, showlegend=False, textfont={"size": 14, "color": Pal.accent2}))
    fig.update_geos(projection_type="natural earth", projection_rotation={"lon": MAP_CENTER_LON}, lataxis_range=list(MAP_LAT_RANGE), showframe=False, showcoastlines=False, landcolor="#EEEEEE", bgcolor="white")
    fig.update_layout(coloraxis_colorbar={"title": "Median lương (USD)", "tickformat": ",.0f", "len": 0.6})
    export_table(table.drop(columns=[Col.COUNTRY]), "f7_1")
    return style_plotly(fig, note), note


def fig_f7_2(table: pd.DataFrame):
    """f7_2: xếp hạng median lương: top, Việt Nam và nhóm thấp nhất."""
    rank = int(table.index[table[Col.COUNTRY] == VIETNAM][0]) + 1
    vn = table.iloc[rank - 1]
    half = "nửa dưới" if rank > len(table) / 2 else "nửa trên"
    picked = pd.concat([table.head(TOP_RANK), table.iloc[[rank - 1]], table.tail(BOTTOM_RANK)]).drop_duplicates(Col.COUNTRY)
    note = Note(
        "f7_2", f"Việt Nam xếp thứ {rank}/{len(table)} nước về median lương ({fmt_usd(vn['median'])}), mẫu chỉ {int(vn['n'])} người",
        f"Trong {len(table)} nước đủ mẫu, Việt Nam ở {half} bảng xếp hạng (median {fmt_usd(vn['median'])}). "
        f"Thanh sai số cho thấy khoảng tin cậy của Việt Nam rất rộng ({fmt_int(vn['lo'])}–{fmt_int(vn['hi'])} USD), nên thứ hạng có thể thay đổi nhiều.",
        "Kỳ vọng lương nên so với mức sống và chi phí tại chỗ, không so trực tiếp bằng USD danh nghĩa với Mỹ hay châu Âu.",
        sal_footer(int(table.n.sum()), f"{TOP_RANK} nước cao nhất, Việt Nam và {BOTTOM_RANK} nước thấp nhất trong {len(table)} nước đủ mẫu; thanh sai số là khoảng tin cậy 95%."),
        int(table.n.sum()))
    plot = picked.iloc[::-1]
    colors = [Pal.accent2 if c == VIETNAM else Pal.accent for c in plot[Col.COUNTRY]]
    fig, ax = new_fig(note, left=0.20)
    err = np.vstack([plot["median"] - plot.lo, plot.hi - plot["median"]])
    ax.barh(plot["name"], plot["median"], xerr=err, color=colors, height=BAR_HEIGHT, error_kw={"ecolor": "#333333", "capsize": 2, "linewidth": 0.8})
    for idx, row in enumerate(plot.itertuples()):
        ax.text(row.hi + table["median"].max() * 0.01, idx, f"{fmt_int(row.median)} (n={fmt_int(row.n)})", va="center", fontsize=6.5)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_xlabel("Median lương (USD)")
    ax.set_xlim(0, table["hi"].max() * 1.25)
    thousands_axis(ax)
    export_table(picked.drop(columns=[Col.COUNTRY]), "f7_2")
    return fig, note


# %%
by_country = country_table(df_sal, countries)

# %%
finish(*fig_f7_1(by_country))

# %%
finish(*fig_f7_2(by_country))
