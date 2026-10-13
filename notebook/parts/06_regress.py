# %% [markdown]
# ## 6. Q6 (tiếp) – Hồi quy kiểm chứng: lương phụ thuộc vào đâu?
# Giả thuyết cần kiểm chứng: **quốc gia và kinh nghiệm đi cùng chênh lệch lương nhiều hơn ngôn ngữ lập trình**.
# Ta so sánh độ phù hợp (R²) của các mô hình `log(lương)` với từng nhóm biến, rồi xem hệ số của ngôn ngữ sau khi đã cố định quốc gia và kinh nghiệm.
# Đây là mô hình mô tả, không chứng minh quan hệ nhân quả; `log(lương)` để hệ số đọc được như % chênh lệch.

# %%
import statsmodels.formula.api as smf

REG_LANGS = 15
Z_CRIT = 1.96
SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
HC_TYPE = "HC3"


@dataclass(frozen=True)
class ModelSpec:
    """Một mô hình hồi quy: nhãn hiển thị và vế phải của công thức."""
    label: str
    rhs: str


@dataclass
class RegResult:
    """Kết quả hồi quy: R² từng mô hình, hệ số ngôn ngữ và kiểm định nhóm biến."""
    r2: pd.DataFrame
    effects: pd.DataFrame
    f_pvalue: float
    n: int


def reg_frame(df: pd.DataFrame, names: list):
    """Dựng bảng hồi quy: log lương, nước, kinh nghiệm và cột 0/1 cho từng ngôn ngữ phổ biến."""
    base = df[df[Col.COUNTRY].isin(names)].dropna(subset=[Col.WORKEXP, Col.LANG_HAVE])[[Col.ID, Col.COUNTRY, Col.WORKEXP, Col.SAL, Col.LANG_HAVE]].copy()
    longer = explode_multi(base, Col.LANG_HAVE)
    top = longer[Col.VALUE].value_counts().head(REG_LANGS).index.tolist()
    flags = pd.crosstab(longer[Col.ID], longer[Col.VALUE])[top].clip(upper=1)
    flags.columns = [f"L{i}" for i in range(len(top))]
    frame = base.set_index(Col.ID).join(flags).fillna(0)
    frame["ly"] = np.log(frame[Col.SAL])
    frame["lexp"] = np.log1p(frame[Col.WORKEXP])
    return frame, top, list(flags.columns)


def fit_models(frame: pd.DataFrame, lang_cols: list) -> dict:
    """Ước lượng các mô hình OLS."""
    langs = " + ".join(lang_cols)
    specs = (
        ModelSpec("Chỉ ngôn ngữ", langs),
        ModelSpec("Chỉ kinh nghiệm", "lexp"),
        ModelSpec("Chỉ quốc gia", f"C({Col.COUNTRY})"),
        ModelSpec("Quốc gia + kinh nghiệm", f"C({Col.COUNTRY}) + lexp"),
        ModelSpec("Quốc gia + kinh nghiệm + ngôn ngữ", f"C({Col.COUNTRY}) + lexp + {langs}"),
    )
    return {spec.label: smf.ols(f"ly ~ {spec.rhs}", frame).fit() for spec in specs}


def run_regression(df: pd.DataFrame, names: list) -> RegResult:
    """Chạy toàn bộ phân tích hồi quy và gom kết quả."""
    frame, top, lang_cols = reg_frame(df, names)
    models = fit_models(frame, lang_cols)
    labels = list(models)
    full, base = models[labels[-1]], models[labels[-2]]
    robust = smf.ols(full.model.formula, frame).fit(cov_type=HC_TYPE)
    effects = []
    for name, col in zip(top, lang_cols):
        coef, se = robust.params[col], robust.bse[col]
        effects.append({"lang": name, "pct": (np.exp(coef) - 1) * 100,
                        "lo": (np.exp(coef - Z_CRIT * se) - 1) * 100, "hi": (np.exp(coef + Z_CRIT * se) - 1) * 100})
    r2 = pd.DataFrame({"model": labels, "r2": [models[k].rsquared for k in labels]})
    return RegResult(r2, pd.DataFrame(effects).sort_values("pct"), float(full.compare_f_test(base)[1]), int(full.nobs))


# %%
reg = run_regression(df_sal, countries)
display(reg.r2.round(3))
print(f"n = {fmt_int(reg.n)} | p-value kiểm định F cho nhóm {REG_LANGS} ngôn ngữ: {reg.f_pvalue:.3g}")


# %%
def fmt_sci(value: float) -> str:
    """Số rất nhỏ dạng khoa học kiểu 3 × 10⁻¹⁹⁵."""
    mantissa, exponent = f"{value:.0e}".split("e")
    return f"{mantissa} × 10{str(int(exponent)).translate(SUPERSCRIPT)}"


def fig_f6_3(result: RegResult):
    """f6_3: R² của các mô hình, tách phần giải thích của quốc gia, kinh nghiệm và ngôn ngữ."""
    r2 = result.r2.set_index("model").r2
    only_lang, only_exp, only_country, country_exp, full = r2.iloc[0], r2.iloc[1], r2.iloc[2], r2.iloc[3], r2.iloc[4]
    supported = only_country > only_lang and (full - country_exp) < (country_exp - only_country)
    verdict = ("Giả thuyết được ủng hộ: để dự đoán lương, biết người đó ở nước nào và có bao nhiêu năm kinh nghiệm quan trọng hơn nhiều so với biết họ dùng ngôn ngữ gì."
               if supported else "Giả thuyết không được ủng hộ rõ: phần giải thích thêm của ngôn ngữ không nhỏ hơn phần của quốc gia và kinh nghiệm.")
    note = Note(
        "f6_3", f"Quốc gia một mình giải thích {fmt_pct(only_country * 100, 0)} biến thiên lương; thêm {REG_LANGS} ngôn ngữ chỉ cộng {fmt_num((full - country_exp) * 100)} điểm phần trăm",
        f"R² của mô hình chỉ có ngôn ngữ là {fmt_pct(only_lang * 100)}, chỉ kinh nghiệm {fmt_pct(only_exp * 100)}, chỉ quốc gia {fmt_pct(only_country * 100)}. "
        f"Thêm kinh nghiệm vào quốc gia tăng R² lên {fmt_pct(country_exp * 100)}, thêm ngôn ngữ chỉ tăng thêm {fmt_num((full - country_exp) * 100)} điểm phần trăm (kiểm định F cho nhóm ngôn ngữ: p = {fmt_sci(result.f_pvalue)}).",
        verdict + " Đây là mô hình mô tả, không chứng minh nhân quả.",
        sal_footer(result.n, f"Hồi quy OLS trên log(lương); nước đủ {Cfg.min_country_n} dòng; {REG_LANGS} ngôn ngữ phổ biến nhất; kinh nghiệm dùng log(1 + WorkExp)."), result.n)
    fig, ax = new_fig(note, left=0.24)
    values = (r2 * 100)[::-1]
    values.index = [name.replace(" + ngôn ngữ", "\n+ ngôn ngữ") for name in values.index]
    colors = [Pal.accent if "+ ngôn ngữ" in name else Pal.neutral for name in values.index]
    ax.barh(values.index, values.to_numpy(), color=colors, height=BAR_HEIGHT)
    annotate_bars_h(ax, values.to_numpy(), [fmt_pct(v) for v in values])
    ax.set_xlabel("R² (% biến thiên của log(lương) được giải thích)")
    ax.set_xlim(0, values.max() * 1.15)
    export_table(result.r2, "f6_3")
    return fig, note


def fig_f6_4(result: RegResult):
    """f6_4: tác động của từng ngôn ngữ lên lương sau khi cố định quốc gia và kinh nghiệm."""
    eff = result.effects
    sig = eff[(eff.lo > 0) | (eff.hi < 0)]
    note = Note(
        "f6_4", f"Sau khi cố định nước và kinh nghiệm, chênh lệch lương theo ngôn ngữ chỉ từ {fmt_pct(eff.pct.min(), 0)} đến {fmt_pct(eff.pct.max(), 0)}",
        f"Hệ số của {len(eff)} ngôn ngữ nằm trong khoảng {fmt_pct(eff.pct.min())} đến {fmt_pct(eff.pct.max())} so với người không dùng ngôn ngữ đó. "
        f"{len(sig)}/{len(eff)} ngôn ngữ có khoảng tin cậy 95% không chứa 0" + (f": {', '.join(sig.sort_values('pct', ascending=False).lang)}." if len(sig) else "."),
        f"Chênh lệch lương đi cùng việc dùng một ngôn ngữ (tối đa {fmt_pct(max(abs(eff.pct.min()), abs(eff.pct.max())), 0)}) nhỏ hơn nhiều so với chênh lệch giữa các nước ở bản đồ lương theo nước (hai đại lượng tính khác nhau nên chỉ so sánh tham khảo); chọn ngôn ngữ nên dựa trên mức phổ biến và sở thích hơn là kỳ vọng tăng lương.",
        sal_footer(result.n, "Hệ số từ hồi quy log(lương) có kiểm soát nước và kinh nghiệm, quy ra % chênh lệch so với người không dùng ngôn ngữ đó; thanh là khoảng tin cậy 95% (sai số chuẩn HC3)."), result.n)
    fig, ax = new_fig(note, left=0.17)
    err = np.vstack([eff.pct - eff.lo, eff.hi - eff.pct])
    colors = [Pal.accent if (lo > 0 or hi < 0) else Pal.neutral for lo, hi in zip(eff.lo, eff.hi)]
    ax.errorbar(eff.pct, eff.lang, xerr=err, fmt="none", ecolor="#333333", capsize=2, linewidth=1, zorder=2)
    ax.scatter(eff.pct, eff.lang, color=colors, s=DOT_SIZE, zorder=3)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Chênh lệch lương khi dùng ngôn ngữ (%), đã kiểm soát nước và kinh nghiệm")
    ax.tick_params(axis="y", labelsize=7)
    export_table(eff, "f6_4")
    return fig, note


# %%
finish(*fig_f6_3(reg))

# %%
finish(*fig_f6_4(reg))
