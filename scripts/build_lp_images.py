from pathlib import Path
from math import cos, sin, pi
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
OUT = ASSET_DIR / "lp"
OUT.mkdir(parents=True, exist_ok=True)

W = 750
NAVY = "#003d90"
BLUE = "#0085d5"
SKY = "#14a9e5"
RED = "#e60012"
DARK_RED = "#8e0008"
YELLOW = "#ffe600"
GOLD = "#d1a33a"
BLACK = "#111111"
WHITE = "#ffffff"
CREAM = "#fff5d6"

FONT_CANDIDATES = {
    "w8": [
        "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ],
    "w6": [
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ],
    "w4": [
        "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ],
}


def font(size, weight="w8"):
    for p in FONT_CANDIDATES[weight]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def text_size(draw, text, f, stroke_width=0):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke_width)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw, xy, text, f, fill, stroke=0, stroke_fill=BLACK, anchor="mm", spacing=8):
    draw.multiline_text(
        xy,
        text,
        font=f,
        fill=fill,
        anchor=anchor,
        align="center",
        spacing=spacing,
        stroke_width=stroke,
        stroke_fill=stroke_fill,
    )


def left_text(draw, xy, text, f, fill, stroke=0, stroke_fill=BLACK, spacing=8):
    draw.multiline_text(
        xy,
        text,
        font=f,
        fill=fill,
        spacing=spacing,
        stroke_width=stroke,
        stroke_fill=stroke_fill,
    )


def wrap_text(draw, text, f, max_width):
    lines = []
    current = ""
    for ch in text:
        if ch == "\n":
            lines.append(current)
            current = ""
            continue
        cand = current + ch
        if text_size(draw, cand, f)[0] <= max_width or not current:
            current = cand
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return "\n".join(lines)


def cover(path, size, focus_y=0.5):
    img = Image.open(path).convert("RGB")
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - tw) // 2
    y = int((nh - th) * focus_y)
    return img.crop((x, y, x + tw, y + th))


def paste_tint(base, photo, alpha=120, color=None):
    layer = photo.convert("RGBA")
    if color:
        tint = Image.new("RGBA", layer.size, color)
        layer = Image.blend(layer, tint, 0.25)
    layer.putalpha(alpha)
    base.alpha_composite(layer)


def shadow_rect(draw, box, fill=WHITE, outline=BLACK, width=5, radius=12, shadow=(9, 9), shadow_fill=(0, 0, 0, 90)):
    x1, y1, x2, y2 = box
    sx, sy = shadow
    draw.rounded_rectangle((x1 + sx, y1 + sy, x2 + sx, y2 + sy), radius=radius, fill=shadow_fill)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def speed_bg(h, center=(375, 430), base=WHITE, accent=YELLOW):
    img = Image.new("RGBA", (W, h), base)
    d = ImageDraw.Draw(img)
    cx, cy = center
    for i in range(72):
        a1 = 2 * pi * i / 72
        a2 = 2 * pi * (i + 0.42) / 72
        r = 1100
        color = accent if i % 2 == 0 else "#fff9ae"
        poly = [(cx, cy), (cx + r * cos(a1), cy + r * sin(a1)), (cx + r * cos(a2), cy + r * sin(a2))]
        d.polygon(poly, fill=color)
    for i in range(36):
        a = 2 * pi * i / 36
        r = 1000
        d.line((cx, cy, cx + r * cos(a), cy + r * sin(a)), fill="#1f1f1f", width=2)
    overlay = Image.new("RGBA", (W, h), (255, 255, 255, 86))
    img.alpha_composite(overlay)
    return img


def top_blue_band(d, text, y=0, h=76):
    d.polygon([(0, y), (W, y), (W - 20, y + h), (20, y + h)], fill=NAVY, outline=BLACK)
    d.line((12, y + h - 8, W - 12, y + h - 8), fill=BLUE, width=5)
    center_text(d, (W // 2, y + h // 2 - 3), text, font(35), WHITE, stroke=3, stroke_fill=BLACK)


def tag_row(d, tags, y, x=25, gap=12):
    tag_w = (W - x * 2 - gap * (len(tags) - 1)) // len(tags)
    for i, t in enumerate(tags):
        bx = x + i * (tag_w + gap)
        shadow_rect(d, (bx, y, bx + tag_w, y + 57), fill=BLACK, outline=WHITE, width=3, radius=8, shadow=(4, 4))
        center_text(d, (bx + tag_w / 2, y + 28), t, font(26), YELLOW, stroke=2, stroke_fill=BLACK)


def brush(d, box, fill=NAVY, outline=WHITE):
    x1, y1, x2, y2 = box
    poly = [
        (x1, y1 + 12), (x2 - 15, y1), (x2, y1 + 28),
        (x2 - 8, y2 - 8), (x1 + 18, y2), (x1, y2 - 24)
    ]
    d.polygon(poly, fill=fill)
    d.line(poly + [poly[0]], fill=outline, width=4)


def badge(d, cx, cy, r, fill, lines, sizes=None, icon=None):
    for i, c in enumerate(["#7a4b00", "#f6d778", GOLD]):
        d.ellipse((cx - r - 5 + i * 2, cy - r - 5 + i * 2, cx + r + 5 - i * 2, cy + r + 5 - i * 2), fill=c)
    d.ellipse((cx - r + 9, cy - r + 9, cx + r - 9, cy + r - 9), fill=fill, outline="#8b5b00", width=3)
    sizes = sizes or [27, 43, 25]
    total = len(lines)
    y = cy - 42 if total >= 3 else cy - 28
    for idx, line in enumerate(lines):
        fsize = sizes[min(idx, len(sizes) - 1)]
        fillc = YELLOW if idx == 1 else WHITE
        center_text(d, (cx, y + idx * 42), line, font(fsize), fillc, stroke=3, stroke_fill=BLACK, spacing=0)


def save(img, name):
    path = OUT / name
    img.convert("RGB").save(path, quality=95)
    print(path)


def fv_main():
    h = 760
    img = speed_bg(h, center=(375, 410))
    photo = cover(ASSET_DIR / "hero-direct.png", (W, h), focus_y=0.28)
    paste_tint(img, photo, alpha=105, color=(255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    tag_row(d, ["施工管理", "現場監督", "職人採用", "有資格者採用"], 22)

    shadow_rect(d, (32, 112, 310, 330), fill=WHITE, outline=BLACK, width=5, radius=10, shadow=(8, 8))
    d.rectangle((38, 119, 304, 176), fill=RED)
    center_text(d, (171, 148), "応募", font(38), WHITE)
    center_text(d, (171, 254), "100人", font(86), RED, stroke=4, stroke_fill="#8b4b00")

    center_text(d, (375, 250), "×", font(88), BLACK)

    shadow_rect(d, (440, 112, 718, 330), fill=WHITE, outline=BLACK, width=5, radius=10, shadow=(8, 8))
    d.rectangle((446, 119, 712, 176), fill=RED)
    center_text(d, (579, 148), "応募単価", font(36), WHITE)
    center_text(d, (579, 254), "1000円", font(78), RED, stroke=4, stroke_fill="#8b4b00")

    d.polygon([(0, 350), (750, 327), (721, 560), (20, 594)], fill="#fffef9", outline=BLACK)
    center_text(d, (W // 2, 452), "＝10万円!?", font(132), RED, stroke=5, stroke_fill="#8b4b00")

    brush(d, (20, 610, 730, 738), fill=NAVY)
    center_text(
        d,
        (W // 2, 674),
        "「施工管理でそんな応募数、あるわけない」\nと思った会社ほど、一度だけ見てください。",
        font(30),
        WHITE,
        stroke=2,
        stroke_fill=BLACK,
        spacing=9,
    )
    save(img, "01-fv-main.png")


def fv_badges():
    h = 520
    img = Image.new("RGBA", (W, h), WHITE)
    d = ImageDraw.Draw(img)
    photo = cover(ASSET_DIR / "cta-direct.png", (W, 320), focus_y=0.45)
    img.alpha_composite(photo.convert("RGBA"), (0, 170))
    d.rectangle((0, 0, W, 210), fill=WHITE)
    for x in range(0, W, 18):
        d.line((x, 0, x - 180, 240), fill="#ffd33a", width=3)
    badge(d, 122, 110, 76, RED, ["定額", "10万円台〜"], sizes=[25, 27])
    badge(d, 292, 110, 76, NAVY, ["成果報酬", "0円"], sizes=[25, 44])
    badge(d, 462, 110, 76, "#0d7d37", ["最短", "3日", "開始"], sizes=[26, 44, 23])
    badge(d, 632, 110, 76, RED, ["月100応募", "も", "狙える"], sizes=[22, 26, 30])
    d.rounded_rectangle((30, 398, 720, 500), radius=22, fill=(255, 255, 255, 235), outline="#d8d8d8", width=2)
    center_text(
        d,
        (W // 2, 448),
        "※応募数・応募単価は職種、地域、条件、時期により変動します。\n採用保証ではありません。",
        font(24, "w6"),
        BLACK,
        spacing=8,
    )
    save(img, "02-fv-badges.png")


def cta():
    h = 390
    img = Image.new("RGBA", (W, h), RED)
    d = ImageDraw.Draw(img)
    for y in range(-h, h, 34):
        d.line((0, y, W, y + W), fill="#ff534f", width=13)
    photo = cover(ASSET_DIR / "cta-direct.png", (W, h), focus_y=0.45)
    paste_tint(img, photo, alpha=70)
    center_text(d, (W // 2, 55), "【初月限定】最大100,000円割引!", font(38), YELLOW, stroke=3, stroke_fill=BLACK)
    d.rounded_rectangle((118, 96, 632, 145), radius=25, fill=BLACK)
    center_text(d, (W // 2, 120), "毎月5社限定", font(28), WHITE)
    center_text(d, (W // 2, 188), "ご相談は完全無料!", font(38), WHITE, stroke=3, stroke_fill=BLACK)
    shadow_rect(d, (58, 230, 692, 334), fill=YELLOW, outline=BLACK, width=5, radius=52, shadow=(0, 9), shadow_fill=(80, 0, 0, 170))
    center_text(d, (W // 2, 282), "建設採用の戦略相談を受ける", font(34), BLACK)
    save(img, "03-cta.png")


def doubt():
    h = 720
    img = Image.new("RGBA", (W, h), CREAM)
    d = ImageDraw.Draw(img)
    top_blue_band(d, "媒体選定で損していませんか？", h=82)
    center_text(d, (W // 2, 185), "これ以上、採用に時間とお金を\n犠牲にするの、\nもう終わりにしませんか？", font(44), BLACK, stroke=2, stroke_fill=WHITE, spacing=12)
    shadow_rect(d, (45, 335, 705, 655), fill=WHITE, outline=BLACK, width=5, radius=10, shadow=(9, 9))
    d.rectangle((65, 358, 685, 430), fill=NAVY)
    center_text(d, (W // 2, 393), "媒体は使います。", font(38), WHITE)
    center_text(d, (W // 2, 472), "でも、媒体ありきでは進めません。", font(36), RED, stroke=2, stroke_fill="#ffd7d7")
    body = "問題は媒体そのものではありません。採用会社側の情報格差で「高い媒体」「成果報酬」「よくわからない運用費」を積まれ、応募単価の勝ち筋が見えないままお金だけ溶けていくことです。"
    left_text(d, (82, 525), wrap_text(d, body, font(24, "w6"), 586), font(24, "w6"), BLACK, spacing=8)
    save(img, "04-doubt.png")


def proof():
    h = 1040
    img = Image.new("RGBA", (W, h), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 230), fill=NAVY)
    center_text(d, (W // 2, 62), "圧倒的実績", font(60), YELLOW, stroke=4, stroke_fill=BLACK)
    center_text(d, (W // 2, 128), "建設を含む複数業界で応募獲得を支援", font(27), WHITE, stroke=2, stroke_fill=BLACK)
    metrics = [("累計支援実績", "700社以上"), ("契約継続率", "95%"), ("顧客満足度", "98%")]
    x = 35
    for label, num in metrics:
        shadow_rect(d, (x, 205, x + 210, 385), fill=WHITE, outline=BLACK, width=4, radius=10, shadow=(6, 6))
        center_text(d, (x + 105, 245), label, font(24), NAVY)
        center_text(d, (x + 105, 315), num, font(48), RED, stroke=2, stroke_fill="#ffd2d2")
        x += 235
    d.rounded_rectangle((32, 430, 718, 578), radius=16, fill=WHITE, outline=BLACK, width=4)
    center_text(d, (W // 2, 465), "支援実績ロゴ掲載予定", font(28), BLACK)
    for i in range(6):
        bx = 64 + (i % 3) * 210
        by = 500 + (i // 3) * 38
        d.rounded_rectangle((bx, by, bx + 160, by + 26), radius=13, fill="#f2f2f2", outline="#d0d0d0")
    center_text(d, (W // 2, 642), "建設系採用の応募単価例", font(40), YELLOW, stroke=3, stroke_fill=BLACK)
    costs = [("施工管理", "2,400円〜"), ("現場作業員", "980円〜"), ("電気工事士", "1,900円〜"), ("CADオペ", "1,200円〜")]
    for i, (label, price) in enumerate(costs):
        bx = 52 + (i % 2) * 340
        by = 695 + (i // 2) * 130
        shadow_rect(d, (bx, by, bx + 300, by + 100), fill=WHITE, outline=BLACK, width=4, radius=10, shadow=(6, 6))
        center_text(d, (bx + 150, by + 30), label, font(26), BLACK)
        center_text(d, (bx + 150, by + 70), price, font(36), RED, stroke=2, stroke_fill="#ffe2e2")
    center_text(d, (W // 2, 975), "※掲載前に職種、地域、条件ごとに試算します。", font(22, "w6"), WHITE)
    save(img, "05-proof.png")


def worries():
    h = 1120
    img = Image.new("RGBA", (W, h), CREAM)
    d = ImageDraw.Draw(img)
    top_blue_band(d, "こんなお悩みありませんか？", h=90)
    items = [
        "施工管理の求人を出しても、応募がほとんど来ない",
        "人材紹介の成果報酬が高すぎて、1名採るだけで利益が飛ぶ",
        "Indeedや求人ボックスを使っているのに、何を直せばいいかわからない",
        "職人・現場監督・有資格者に刺さる求人票が作れない",
        "現場が忙しく、応募者対応やスカウトに時間を割けない",
        "媒体会社に言われるまま課金して、結局応募単価が合わない",
    ]
    y = 135
    for item in items:
        shadow_rect(d, (46, y, 704, y + 126), fill=WHITE, outline=BLACK, width=4, radius=8, shadow=(6, 6), shadow_fill=(230, 0, 18, 70))
        d.ellipse((68, y + 38, 116, y + 86), fill=RED)
        center_text(d, (92, y + 62), "!", font(34), WHITE)
        left_text(d, (134, y + 31), wrap_text(d, item, font(26), 520), font(26), BLACK, spacing=7)
        y += 152
    save(img, "06-worries.png")


def solution():
    h = 870
    img = Image.new("RGBA", (W, h), BLACK)
    d = ImageDraw.Draw(img)
    photo = cover(ASSET_DIR / "hero-direct.png", (W, h), focus_y=0.6)
    paste_tint(img, photo, alpha=86)
    center_text(d, (W // 2, 85), "そのお悩み、ぜーんぶ", font(38), YELLOW, stroke=3, stroke_fill=BLACK)
    center_text(d, (W // 2, 188), "まるっと建設採用が\n10万円台〜で", font(58), WHITE, stroke=4, stroke_fill=BLACK, spacing=10)
    center_text(d, (W // 2, 315), "解決できちゃうかも!?", font(48), RED, stroke=4, stroke_fill=WHITE)
    shadow_rect(d, (45, 400, 705, 600), fill=WHITE, outline=BLACK, width=5, radius=10, shadow=(9, 9))
    center_text(d, (W // 2, 452), "採用の「応募が来ない」を、まず潰します。", font(31), RED)
    body = "求人票作成、無料求人媒体の最適化、スカウト、採用SNS、候補者対応、改善レポートまで、建設採用で応募数を増やすための打ち手をまとめて実行します。"
    left_text(d, (78, 508), wrap_text(d, body, font(23, "w6"), 596), font(23, "w6"), BLACK, spacing=7)
    d.rounded_rectangle((44, 665, 706, 818), radius=18, fill=NAVY, outline=WHITE, width=4)
    center_text(d, (W // 2, 705), "対応可能職種", font(30), YELLOW, stroke=2, stroke_fill=BLACK)
    center_text(d, (W // 2, 765), "施工管理 / 現場監督 / 職人 / 電気工事士\nCAD / 設計 / 積算 / 建設営業 ほか", font(25), WHITE, spacing=8)
    save(img, "07-solution.png")


def jobs():
    h = 960
    img = Image.new("RGBA", (W, h), WHITE)
    d = ImageDraw.Draw(img)
    center_text(d, (W // 2, 70), "建設業界の主要職種から\n採用難のニッチ職種まで対応", font(39), NAVY, stroke=2, stroke_fill="#dff1ff", spacing=8)
    tags = ["建築施工管理", "土木施工管理", "現場監督", "電気工事士", "管工事施工管理", "設備職人", "大工", "鳶職", "左官", "塗装", "防水", "内装", "重機オペレーター", "CADオペレーター", "設計", "積算", "安全管理", "建設営業"]
    for i, t in enumerate(tags):
        bx = 35 + (i % 2) * 350
        by = 170 + (i // 2) * 80
        shadow_rect(d, (bx, by, bx + 315, by + 58), fill="#fff2a5", outline=BLACK, width=3, radius=8, shadow=(4, 4), shadow_fill=(230, 0, 18, 60))
        center_text(d, (bx + 157, by + 29), t, font(24), BLACK)
    save(img, "08-jobs.png")


def secrets():
    h = 1420
    img = Image.new("RGBA", (W, h), RED)
    d = ImageDraw.Draw(img)
    for y in range(0, h, 28):
        d.line((0, y, W, y - W), fill="#ff4c47", width=8)
    center_text(d, (W // 2, 86), "なぜそんなに応募を集められるの？", font(39), YELLOW, stroke=3, stroke_fill=BLACK)
    center_text(d, (W // 2, 154), "選ばれる秘訣3選", font(62), WHITE, stroke=4, stroke_fill=BLACK)
    cards = [
        ("01", "代行費10万円台〜のみ", "高額な成果報酬や不要な媒体費を前提にせず、まずは低コストで応募を取りにいく設計を組みます。"),
        ("02", "無料求人媒体のアルゴリズムを取りにいく", "Indeed、求人ボックス、スタンバイ、ハローワークなどを、職種名・エリア・条件別に最適化します。"),
        ("03", "丸投げでOK", "求人票、スカウト文面、媒体運用、採用SNS、候補者対応まで一気通貫。社長が現場から離れる時間を減らします。"),
    ]
    y = 245
    for num, title, body in cards:
        shadow_rect(d, (45, y, 705, y + 330), fill=WHITE, outline=BLACK, width=5, radius=10, shadow=(9, 9))
        d.rectangle((66, y + 24, 180, y + 96), fill=YELLOW, outline=BLACK, width=4)
        center_text(d, (123, y + 60), num, font(42), BLACK)
        center_text(d, (440, y + 62), wrap_text(d, title, font(34), 470), font(34), RED, stroke=2, stroke_fill="#ffe1e1", spacing=5)
        left_text(d, (82, y + 138), wrap_text(d, body, font(26, "w6"), 585), font(26, "w6"), BLACK, spacing=9)
        y += 375
    save(img, "09-secrets.png")


def reason_methods():
    h = 1380
    img = Image.new("RGBA", (W, h), NAVY)
    d = ImageDraw.Draw(img)
    center_text(d, (W // 2, 70), "建設採用に強い理由", font(50), YELLOW, stroke=3, stroke_fill=BLACK)
    cards = [
        ("建設求職者は「給与」だけで動きません。", "現場エリア、直行直帰、出張、夜勤、残業、資格手当、元請け比率、工期の安定性、人間関係、道具支給、社用車、独立支援。候補者が見るポイントが多いからこそ、求人票の作り方で応募数が変わります。"),
        ("「職種 × 地域 × 資格 × 働き方」で検索面を取りにいく。", "施工管理、2級建築施工管理技士、電気工事士、土木、未経験、夜勤なし、直行直帰。候補者が実際に探す言葉から逆算し、媒体ごとに求人タイトルと本文をチューニングします。"),
    ]
    y = 135
    for title, body in cards:
        shadow_rect(d, (45, y, 705, y + 300), fill=WHITE, outline=BLACK, width=5, radius=10, shadow=(9, 9))
        center_text(d, (W // 2, y + 55), wrap_text(d, title, font(31), 600), font(31), RED, spacing=5)
        left_text(d, (80, y + 125), wrap_text(d, body, font(23, "w6"), 585), font(23, "w6"), BLACK, spacing=8)
        y += 330
    d.rectangle((0, 820, W, 1380), fill="#f4f9ff")
    center_text(d, (W // 2, 890), "13の採用手法を\n建設採用向けに実行", font(42), NAVY, stroke=2, stroke_fill=WHITE, spacing=8)
    tags = ["検索エンジン", "Indeed", "求人ボックス", "スタンバイ", "ハローワーク", "スカウト代行", "採用SNS", "建設系媒体", "リファラル", "求人広告", "人材紹介併用", "ダイレクト採用", "採用広報"]
    for i, t in enumerate(tags):
        cols = 2
        bx = 45 + (i % cols) * 335
        by = 1005 + (i // cols) * 70
        shadow_rect(d, (bx, by, bx + 300, by + 50), fill=WHITE, outline=BLACK, width=3, radius=8, shadow=(4, 4), shadow_fill=(0, 80, 180, 60))
        center_text(d, (bx + 150, by + 25), t, font(22), BLACK)
    save(img, "10-reason-methods.png")


def voices_plan():
    h = 1540
    img = Image.new("RGBA", (W, h), CREAM)
    d = ImageDraw.Draw(img)
    top_blue_band(d, "お客様の声・事例", h=82)
    voices = [
        ("建設業 A社", "施工管理歴20年の経験者採用に成功", "有資格者から応募が来ると思っていなかった。応募経路が増え、紹介会社だけに頼らず進められた。", "採用成功 3名 / 6ヶ月"),
        ("設備工事 B社", "職人応募が月40件超まで改善", "現場エリア、資格支援、社用車、残業の見せ方を整理し、未経験と経験者で求人を分けて運用。", "応募単価 1,000円台を狙う設計"),
        ("工務店 C社", "求人公開後すぐに面接候補を確保", "求人票のタイトルと条件の出し方を変更し、通勤圏内の候補者に刺さる導線を再設計。", "短期急募にも対応"),
    ]
    y = 120
    for company, title, body, result in voices:
        shadow_rect(d, (45, y, 705, y + 250), fill=WHITE, outline=BLACK, width=4, radius=10, shadow=(7, 7))
        d.rounded_rectangle((70, y + 24, 230, y + 58), radius=17, fill=BLACK)
        center_text(d, (150, y + 41), company, font(19), WHITE)
        center_text(d, (W // 2, y + 94), wrap_text(d, title, font(29), 595), font(29), RED, spacing=6)
        left_text(d, (76, y + 132), wrap_text(d, body, font(21, "w6"), 590), font(21, "w6"), BLACK, spacing=7)
        d.rectangle((65, y + 202, 685, y + 232), fill=YELLOW)
        center_text(d, (W // 2, y + 217), result, font(20), BLACK)
        y += 280
    d.rectangle((0, 990, W, h), fill=WHITE)
    center_text(d, (W // 2, 1060), "今だけのトライアル価格", font(42), NAVY, stroke=2, stroke_fill="#dff1ff")
    shadow_rect(d, (52, 1115, 698, 1465), fill="#fffdf2", outline=BLACK, width=5, radius=12, shadow=(9, 9))
    d.rounded_rectangle((250, 1138, 500, 1185), radius=24, fill=RED, outline=BLACK, width=3)
    center_text(d, (W // 2, 1161), "今月残り4社", font(25), WHITE)
    center_text(d, (W // 2, 1250), "月額 10万円〜", font(66), RED, stroke=3, stroke_fill="#ffdede")
    center_text(d, (W // 2, 1298), "税抜", font(22), BLACK)
    items = "採用要件ヒアリング / 求人票作成 / 媒体運用\nスカウト文面作成 / 候補者対応 / 改善レポート"
    center_text(d, (W // 2, 1370), items, font(24, "w6"), BLACK, spacing=8)
    d.rounded_rectangle((205, 1410, 545, 1452), radius=21, fill="#e9f3ff", outline=BLACK, width=3)
    center_text(d, (W // 2, 1431), "手頃で会社助かる〜!", font(24), BLACK)
    save(img, "11-voices-plan.png")


def faq_final():
    h = 1100
    img = Image.new("RGBA", (W, h), WHITE)
    d = ImageDraw.Draw(img)
    top_blue_band(d, "よくある質問", h=90)
    qs = [
        ("必ず採用できますか？", "採用保証ではありません。ただし応募数、応募単価、面接化率を見ながら、採用可能性が上がる打ち手を最大限実行します。"),
        ("採用媒体は使いますか？", "使います。無料媒体を中心に、職種・地域・予算に合わせて選定します。有料媒体が効果的な場合も、事前相談のうえ進めます。"),
        ("地方の建設会社でも依頼できますか？", "全国対応可能です。通勤圏、競合求人、現場エリア、資格要件を踏まえて運用します。"),
        ("丸投げできますか？", "求人票作成、媒体運用、スカウト、応募者対応、改善レポートまで対応可能です。面接や採用判断は貴社にお願いしています。"),
    ]
    y = 125
    for q, a in qs:
        shadow_rect(d, (45, y, 705, y + 160), fill=WHITE, outline=BLACK, width=4, radius=8, shadow=(6, 6))
        d.rectangle((45, y, 705, y + 54), fill="#fff2a5", outline=BLACK, width=4)
        left_text(d, (66, y + 13), "Q. " + wrap_text(d, q, font(24), 560), font(24), BLACK, spacing=5)
        left_text(d, (66, y + 76), "A. " + wrap_text(d, a, font(20, "w6"), 585), font(20, "w6"), BLACK, spacing=6)
        y += 185
    d.rectangle((0, 900, W, h), fill=BLACK)
    center_text(d, (W // 2, 960), "応募100人を狙う採用戦略、", font(34), YELLOW, stroke=2, stroke_fill=BLACK)
    center_text(d, (W // 2, 1014), "まずは無料で見ます。", font(44), WHITE, stroke=3, stroke_fill=BLACK)
    save(img, "12-faq-final.png")


if __name__ == "__main__":
    fv_main()
    fv_badges()
    cta()
    doubt()
    proof()
    worries()
    solution()
    jobs()
    secrets()
    reason_methods()
    voices_plan()
    faq_final()
