# %% [markdown]
# ## 7. Q9 – AI và kỹ năng còn giá trị trong 3–5 năm tới
# Câu hỏi mở `AIOpen`: "Looking ahead 3–5 years, what skills do you believe will remain valuable…". Ta đếm số câu trả lời chứa mỗi từ (một câu chỉ tính một lần cho mỗi từ),
# bỏ từ dừng tiếng Anh và một số từ chung chung. Wordcloud chỉ cho biết tần suất từ, không cho biết bối cảnh, nên đi kèm bảng tần suất.

# %%
from collections import Counter

from wordcloud import STOPWORDS, WordCloud

TOKEN_RE = re.compile(r"[a-z][a-z+#\-]{2,}|\bai\b|\bml\b")
EXTRA_STOP = frozenset((
    "will", "still", "able", "need", "needs", "good", "don", "even", "use", "new", "things", "thing", "work", "level",
    "know", "also", "like", "one", "would", "can", "much", "many", "just", "get", "make", "way", "lot", "really", "better",
    "best", "skills", "skill", "remain", "valuable", "think", "people", "something", "may", "might", "etc", "bit", "well",
))
MAX_CHARS = 2000
CLOUD_W = 1500
CLOUD_H = 560
CLOUD_WORDS = 80
CLOUD_SCALING = 0.2
CLOUD_MAX_FONT = 150
TOP_WORDS = 20
HIGHLIGHT_WORDS = 5
FOUNDATION_WORDS = frozenset(("understanding", "problem", "solving", "thinking", "design", "architecture", "debugging", "critical", "communication", "knowledge"))
PHRASE_PROBLEM = re.compile(r"problem[- ]solving")
PHRASE_CRITICAL = re.compile(r"critical thinking")


def tokenise(texts: pd.Series) -> list:
    """Tách mỗi câu trả lời thành tập từ viết thường, đã gộp số nhiều và bỏ từ dừng."""
    raw = [set(TOKEN_RE.findall(text[:MAX_CHARS].lower())) for text in texts]
    vocab = set().union(*raw)
    stop = STOPWORDS | EXTRA_STOP
    return [{(w[:-1] if w.endswith("s") and w[:-1] in vocab else w) for w in words} - stop for words in raw]


def word_table(texts: pd.Series) -> pd.DataFrame:
    """Bảng số câu trả lời chứa từng từ."""
    counts = Counter(word for words in tokenise(texts) for word in words)
    table = pd.DataFrame(counts.most_common(), columns=["word", "responses"])
    table["pct"] = table.responses / len(texts) * 100
    return table


def phrase_share(texts: pd.Series, pattern) -> float:
    """Tỷ lệ % câu trả lời chứa một cụm từ."""
    return float(texts.str.lower().str.contains(pattern).mean() * 100)


def cloud_colors(top_words: set):
    """Hàm màu: từ nổi bật dùng màu nhấn phụ, còn lại màu nhấn chính."""
    def pick(word, **_):
        return Pal.accent2 if word in top_words else Pal.accent
    return pick


# %%
def fig_f9_1(table: pd.DataFrame, n: int):
    """f9_1: wordcloud các kỹ năng được cho là còn giá trị."""
    top = table.head(HIGHLIGHT_WORDS)
    hits = [w for w in table.word.head(TOP_WORDS) if w in FOUNDATION_WORDS]
    note = Note(
        "f9_1", f"{', '.join(top.word[:3])} là những từ được nhắc nhiều nhất khi nói về kỹ năng còn giá trị",
        f"Từ '{top.word.iloc[0]}' xuất hiện trong {fmt_pct(top.pct.iloc[0])} số câu trả lời, '{top.word.iloc[1]}' {fmt_pct(top.pct.iloc[1])}, '{top.word.iloc[2]}' {fmt_pct(top.pct.iloc[2])} (trên {fmt_int(n)} câu trả lời). "
        "Wordcloud chỉ phản ánh tần suất từ, không cho biết ngữ cảnh (xem bảng tần suất từ khóa đi kèm).",
        f"Trong {TOP_WORDS} từ đầu có {len(hits)} từ thuộc nhóm năng lực nền tảng do nhóm tự phân loại ({', '.join(hits)}; 'problem' và 'solving' thường đi thành cụm 'problem solving'); đây là ý kiến tự do của người trả lời, không phải dự báo.",
        source_line(n, f"Câu hỏi mở AIOpen; đếm số câu trả lời chứa từ; bỏ từ dừng và từ chung chung; {HIGHLIGHT_WORDS} từ nổi bật tô màu cam."), n)
    cloud = WordCloud(width=CLOUD_W, height=CLOUD_H, background_color="white", max_words=CLOUD_WORDS, random_state=Cfg.seed,
                      color_func=cloud_colors(set(top.word)), prefer_horizontal=0.9, relative_scaling=CLOUD_SCALING, max_font_size=CLOUD_MAX_FONT)
    cloud.generate_from_frequencies(dict(zip(table.word, table.responses)))
    fig, ax = new_fig(note, left=0.02)
    ax.imshow(cloud.to_array(), interpolation="bilinear")
    ax.axis("off")
    return fig, note


def fig_f9_2(table: pd.DataFrame, n: int):
    """f9_2: top từ khóa trong câu trả lời về kỹ năng."""
    top = table.head(TOP_WORDS)[::-1]
    note = Note(
        "f9_2", f"Top {TOP_WORDS} từ khóa: {', '.join(table.word[:4])} dẫn đầu",
        f"{TOP_WORDS} từ đầu có mặt trong từ {fmt_pct(table.pct.iloc[TOP_WORDS - 1], 1)} đến {fmt_pct(table.pct.iloc[0], 1)} số câu trả lời. "
        f"{TOP_WORDS} từ đầu gồm: {', '.join(table.word.head(TOP_WORDS))}.",
        "Bảng tần suất bổ sung bối cảnh cho wordcloud: tỷ lệ phần trăm cho thấy mức độ phổ biến thật của từng từ.",
        source_line(n, f"Câu hỏi mở AIOpen; tỷ lệ = số câu trả lời chứa từ / tổng số câu trả lời; bỏ từ dừng và từ chung chung."), n)
    fig, ax = new_fig(note, left=0.16)
    ax.barh(top.word, top.pct, color=Pal.accent, height=BAR_HEIGHT)
    annotate_bars_h(ax, top.pct.to_numpy(), [fmt_pct(v) for v in top.pct])
    ax.set_xlabel("Tỷ lệ câu trả lời chứa từ (%)")
    ax.set_xlim(0, top.pct.max() * 1.12)
    return fig, note


# %%
open_texts = df_all[Col.AIOPEN].dropna().astype(str)
words = word_table(open_texts)
export_table(words.head(200), "f9_2")
print(f"Số câu trả lời AIOpen: {fmt_int(len(open_texts))} | Số từ khác nhau: {fmt_int(len(words))}")

# %%
finish(*fig_f9_1(words, len(open_texts)))

# %%
finish(*fig_f9_2(words, len(open_texts)))
