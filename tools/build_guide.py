"""학습 교안 PDF 빌더.

저장소의 마크다운 문서(README, docs/lessons, harness, docs/*.md)를 차례로 읽어
docs/하네스_엔지니어링_입문_학습교안.pdf 한 권으로 묶는다.
원고는 따로 없다. 저장소의 md 파일이 곧 원고다. (md 를 고치고 이 스크립트를 다시 실행하면 PDF 가 바뀐다)

    pip install reportlab
    python tools/build_guide.py

필요한 글꼴
  - 맑은 고딕 (Windows 기본)
  - D2Coding (https://github.com/naver/d2codingfont)
    위치는 D2CODING_DIR 환경 변수 또는 tools/fonts/ 에서 찾는다.

지원하는 마크다운
  # 장 / ## 절 / ### 소절, 문단, - 목록, 1. 번호 목록, - [ ] 체크 항목, | 표 |,
  ``` 코드 상자 ```, > 인용 상자, --- (무시), **굵게**, `코드`, [글](링크)
"""

import glob
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Flowable,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "하네스_엔지니어링_입문_학습교안.pdf"
TITLE = "하네스 엔지니어링 입문"
INSTRUCTOR = "김대철"
REPO = "github.com/sinaboro/harness-crud-lab"


# ---------------------------------------------------------------- 글꼴
def find_font(names, dirs):
    """여러 폴더에서 글꼴 파일을 찾는다. names 는 후보 파일 이름(와일드카드 가능) 목록."""
    for d in dirs:
        if not d:
            continue
        for name in names:
            hits = glob.glob(os.path.join(d, "**", name), recursive=True)
            if hits:
                return hits[0]
    raise SystemExit(f"글꼴을 찾을 수 없습니다: {names} (D2CODING_DIR 환경 변수를 확인하세요)")


font_dirs = [os.environ.get("D2CODING_DIR", ""), str(ROOT / "tools" / "fonts"), "C:/Windows/Fonts"]
FONTS = {
    "Body": TTFont("Body", find_font(["malgun.ttf"], font_dirs)),
    "BodyB": TTFont("BodyB", find_font(["malgunbd.ttf"], font_dirs)),
    "Mono": TTFont("Mono", find_font(["D2Coding.ttf", "D2Coding-Ver*.ttf"], font_dirs)),
    "MonoB": TTFont("MonoB", find_font(["D2CodingBold.ttf", "D2CodingBold-Ver*.ttf"], font_dirs)),
}
for font in FONTS.values():
    pdfmetrics.registerFont(font)
pdfmetrics.registerFontFamily("Body", normal="Body", bold="BodyB", italic="Body", boldItalic="BodyB")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="MonoB", italic="Mono", boldItalic="MonoB")

MISSING = set()  # 어느 글꼴에도 없는 글자 (빌드 끝에 알려 준다)


def has_glyph(font_name, ch):
    return ord(ch) in FONTS[font_name].face.charToGlyph


def fallback(text, main, other):
    """main 글꼴에 없는 글자를 other 글꼴로 바꿔 그린다. text 는 이미 escape 된 문자열."""
    out = []
    for ch in text:
        if ord(ch) < 128 or has_glyph(main, ch):
            out.append(ch)
        elif has_glyph(other, ch):
            out.append(f'<font name="{other}">{ch}</font>')
        else:
            MISSING.add(ch)
            out.append("?")
    return "".join(out)


# ---------------------------------------------------------------- 색과 스타일
NAVY = colors.HexColor("#1f3a5f")
BLUE = colors.HexColor("#03588C")
ACCENT = colors.HexColor("#2f8f6b")
LIGHT = colors.HexColor("#eef3f8")
CODE_BG = colors.HexColor("#f6f8fa")
OUT_BG = colors.HexColor("#fbfbf3")
GREY = colors.HexColor("#6b7280")

# 명령을 치는 곳 표시([PS] 등)의 색과 풀이
WHERE = {
    "PS": ("#1d5fa8", "윈도우 PowerShell"),
    "dev": ("#2e7d32", "dev 컨테이너"),
    "AI": ("#8e44ad", "OpenCode 입력 칸"),
    "psql": ("#b9770e", "psql"),
}
# 코드 상자의 왼쪽 띠 색 (언어별)
EDGE = {
    "powershell": "#1d5fa8", "bash": "#2e7d32", "sh": "#2e7d32", "sql": "#b9770e",
    "python": "#03588C", "text": "#9aa3ad", "json": "#9aa3ad", "jsonc": "#03588C",
    "yaml": "#03588C", "html": "#03588C", "javascript": "#03588C", "markdown": "#8e44ad",
}

S = {}
S["body"] = ParagraphStyle("body", fontName="Body", fontSize=9.6, leading=15.5, spaceAfter=4.5)
S["bullet"] = ParagraphStyle("bullet", parent=S["body"], leftIndent=13, bulletIndent=3, spaceAfter=2)
S["bullet2"] = ParagraphStyle("bullet2", parent=S["bullet"], leftIndent=26, bulletIndent=16)
S["h1"] = ParagraphStyle("h1", fontName="BodyB", fontSize=18, leading=24, textColor=colors.white)
S["h2"] = ParagraphStyle("h2", fontName="BodyB", fontSize=13.5, leading=19, textColor=NAVY,
                         spaceBefore=12, spaceAfter=5, keepWithNext=1)
S["h3"] = ParagraphStyle("h3", fontName="BodyB", fontSize=11, leading=16, textColor=BLUE,
                         spaceBefore=8, spaceAfter=3, keepWithNext=1)
S["h4"] = ParagraphStyle("h4", fontName="BodyB", fontSize=9.8, leading=15, textColor=colors.HexColor("#374151"),
                         spaceBefore=5, spaceAfter=2, keepWithNext=1)
S["where"] = ParagraphStyle("where", fontName="BodyB", fontSize=8.2, leading=11, spaceBefore=3,
                            spaceAfter=1.5, keepWithNext=1)
S["cell"] = ParagraphStyle("cell", fontName="Body", fontSize=8.6, leading=12.5)
S["cellh"] = ParagraphStyle("cellh", parent=S["cell"], fontName="BodyB", textColor=colors.white)
S["quote"] = ParagraphStyle("quote", parent=S["body"], fontSize=9.1, leading=14.2, spaceAfter=2)
S["toc1"] = ParagraphStyle("toc1", fontName="BodyB", fontSize=10, leading=16.5, leftIndent=0)
S["toc2"] = ParagraphStyle("toc2", fontName="Body", fontSize=8.6, leading=12.6, leftIndent=16,
                           textColor=colors.HexColor("#374151"))

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
TEXT_W = PAGE_W - 2 * MARGIN


def inline(text):
    """**굵게**, `코드`, [글](링크), *기울임* 을 ReportLab 마크업으로 바꾼다."""
    text = re.sub(r"\[([^\]]+)\]\((?!\s)[^)]*\)", r"\1", text)  # [글](링크) → 글
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            code = fallback(escape(p[1:-1]), "Mono", "Body")
            out.append(f'<font name="Mono" color="#b5245e">{code}</font>')
            continue
        p = re.sub(r"\*\*(.+?)\*\*", "\x01\\1\x02", p)  # **굵게**
        p = re.sub(r"(?<![\*\w])\*([^*\s][^*]*?)\*(?![\*\w])", r"\1", p)  # *기울임* → 그냥 글
        p = fallback(escape(p), "Body", "Mono")
        p = p.replace("\\", '<font name="Mono">\\</font>')  # 맑은 고딕은 \ 를 ₩ 로 그린다
        out.append(p)
    return "".join(out).replace("\x01", "<b>").replace("\x02", "</b>")


def disp_width(s):
    """화면 폭: 한글·한자는 2칸, 나머지는 1칸."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


# ---------------------------------------------------------------- 코드 상자
def code_table(text, lang):
    """코드 한 줄을 표의 한 행으로 만든다. → 쪽이 넘어가도 자연스럽게 나뉜다."""
    text = text.expandtabs(4)
    lines = text.split("\n")
    avail = TEXT_W - 14
    cols = max([disp_width(line) for line in lines] + [1])
    size = max(min(8.2, avail / (cols * 0.5)), 7.0)  # 긴 줄이 있으면 글자를 조금 줄인다
    max_cols = int(avail / (size * 0.5))
    st = ParagraphStyle("c", fontName="Mono", fontSize=size, leading=size * 1.38)
    comment_mark = {"bash": "#", "sh": "#", "powershell": "#", "yaml": "#", "python": "#",
                    "sql": "--", "jsonc": "//", "javascript": "//"}.get(lang)

    def markup(s):
        body = fallback(escape(s), "Mono", "Body").replace(" ", "&nbsp;")
        # 줄 전체가 주석이면 초록색으로
        if comment_mark and s.strip().startswith(comment_mark):
            return f'<font color="#2e7d32">{body}</font>'
        return body

    data = []
    for line in lines:
        while disp_width(line) > max_cols:  # 그래도 길면 줄을 나눈다
            cut, w = 0, 0
            for i, c in enumerate(line):
                w += 2 if unicodedata.east_asian_width(c) in "WF" else 1
                if w > max_cols:
                    cut = i
                    break
            data.append([Paragraph(markup(line[:cut]) or "&nbsp;", st)])
            line = "  " + line[cut:]
        data.append([Paragraph(markup(line) or "&nbsp;", st)])
    is_output = lang in ("text", "json")
    t = Table(data, colWidths=[TEXT_W], splitByRow=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), OUT_BG if is_output else CODE_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, colors.HexColor(EDGE.get(lang, "#9aa3ad"))),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 4),
    ]))
    return t


def quote_box(lines):
    """> 로 시작하는 인용 문단을 왼쪽 띠가 있는 상자로 그린다."""
    inner = []
    para = []

    def flush():
        if para:
            inner.append(Paragraph(inline(" ".join(para)), S["quote"]))
            para.clear()

    for line in lines:
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("- "):
            flush()
            inner.append(Paragraph(inline(s[2:]), S["quote"], bulletText="•"))
        else:
            para.append(s)
    flush()
    t = Table([[inner]], colWidths=[TEXT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7e8")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#e8890c")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    t.spaceBefore, t.spaceAfter = 3, 7
    return [t]


def md_table(rows):
    """마크다운 표를 그린다. 머리 줄이 비어 있으면(| | |) 머리 없는 표로 그린다."""
    rows = [[c.strip().replace("\x00", "|") for c in r.replace("\\|", "\x00").strip().strip("|").split("|")]
            for r in rows]  # \| 는 칸 구분이 아니라 글자 |
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    has_head = any(c for c in rows[0])
    if not has_head:
        rows = rows[1:]
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]

    def plain(c):
        return re.sub(r"[`*]|\]\([^)]*\)", "", c)

    widths = [max(disp_width(plain(r[i])) for r in rows) for i in range(ncol)]
    widths = [min(max(w, 5), 58) + 3 for w in widths]
    total = sum(widths)
    colw = [TEXT_W * w / total for w in widths]
    data = [[Paragraph(inline(c), S["cellh"] if (i == 0 and has_head) else S["cell"]) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=colw, repeatRows=1 if has_head else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d3df")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if has_head:
        style += [("BACKGROUND", (0, 0), (-1, 0), NAVY),
                  ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]
    else:
        style += [("BACKGROUND", (0, 0), (0, -1), LIGHT)]
    t.setStyle(TableStyle(style))
    t.spaceBefore, t.spaceAfter = 2, 8
    return [t]


class ChapterBanner(Flowable):
    """장 제목 띠. 목차와 책갈피에도 등록된다."""

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.para = Paragraph(inline(text), S["h1"])

    def wrap(self, aw, ah):
        self.para.wrap(aw - 24, ah)
        self.height = self.para.height + 26
        return aw, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.roundRect(0, 0, TEXT_W, self.height, 4, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.rect(0, 0, 6, self.height, fill=1, stroke=0)
        self.para.drawOn(c, 16, 12)


# ---------------------------------------------------------------- 문서 템플릿
class GuideDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                         topMargin=MARGIN + 6, bottomMargin=MARGIN, title=f"{TITLE} 학습 교안",
                         author=INSTRUCTOR, subject="AI 에이전트에게 맡겨 만드는 메모 CRUD 프로젝트")
        frame = Frame(MARGIN, MARGIN, TEXT_W, PAGE_H - 2 * MARGIN - 6, id="f",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate("cover", [frame], onPage=self.cover),
                               PageTemplate("body", [frame], onPageEnd=self.decorate)])
        self.chapter = ""

    def beforeDocument(self):
        self.chapter = ""

    def afterFlowable(self, f):
        if isinstance(f, ChapterBanner):
            self.chapter = re.sub(r"<[^>]+>", "", f.text)
            key = f"ch{self.page}{id(f)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(self.chapter, key, level=0)
            if self.chapter != "목차":
                self.notify("TOCEntry", (0, escape(self.chapter), self.page, key))
        elif isinstance(f, Paragraph) and f.style.name == "h2":
            text = f.getPlainText()
            key = f"h2{self.page}{id(f)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=1)
            self.notify("TOCEntry", (1, escape(text), self.page, key))

    def decorate(self, c, doc):
        """본문 쪽의 머리말·꼬리말"""
        c.saveState()
        c.setFont("Body", 7.5)
        c.setFillColor(GREY)
        c.drawString(MARGIN, PAGE_H - MARGIN + 2, self.chapter)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 2, TITLE)
        c.setStrokeColor(colors.HexColor("#d1d9e3"))
        c.setLineWidth(0.5)
        c.line(MARGIN, PAGE_H - MARGIN - 1, PAGE_W - MARGIN, PAGE_H - MARGIN - 1)
        c.line(MARGIN, MARGIN - 7, PAGE_W - MARGIN, MARGIN - 7)
        c.drawString(MARGIN, MARGIN - 16, f"강사 {INSTRUCTOR}")
        c.drawCentredString(PAGE_W / 2, MARGIN - 16, str(doc.page))
        c.drawRightString(PAGE_W - MARGIN, MARGIN - 16, REPO)
        c.restoreState()

    def cover(self, c, doc):
        """표지"""
        c.saveState()
        c.setFillColor(NAVY)
        c.rect(0, PAGE_H * 0.42, PAGE_W, PAGE_H * 0.58, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.rect(0, PAGE_H * 0.42 - 6, PAGE_W, 6, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#f0a500"))
        c.roundRect(MARGIN + 4, PAGE_H - 70 * mm, 34 * mm, 9 * mm, 3, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("BodyB", 11)
        c.drawCentredString(MARGIN + 4 + 17 * mm, PAGE_H - 70 * mm + 3 * mm, "학습 교안")
        c.setFont("BodyB", 34)
        c.drawString(MARGIN + 4, PAGE_H - 96 * mm, "하네스 엔지니어링 입문")
        c.setFont("BodyB", 19)
        c.drawString(MARGIN + 4, PAGE_H - 111 * mm, "AI 에이전트에게 맡기고, 이해하고, 검증해서 저장하는")
        c.drawString(MARGIN + 4, PAGE_H - 121 * mm, "메모 CRUD 프로젝트")
        c.setFont("Body", 11.5)
        c.setFillColor(colors.HexColor("#d6e2f0"))
        c.drawString(MARGIN + 4, PAGE_H - 136 * mm,
                     "Docker · OpenRouter · OpenCode · Python · FastAPI · PostgreSQL · pytest · Git")
        c.drawString(MARGIN + 4, PAGE_H - 144 * mm, "3일 × 8시간 · 12교시 · 초보자 대상 실습 과정")
        c.setFillColor(NAVY)
        c.setFont("BodyB", 15)
        c.drawString(MARGIN + 4, 70 * mm, f"강사  {INSTRUCTOR}")
        c.setFont("Body", 10.5)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawString(MARGIN + 4, 60 * mm, f"작성일  {date.today():%Y.%m.%d}")
        c.drawString(MARGIN + 4, 52 * mm, "실습 환경  Windows + Docker Desktop (모든 도구는 컨테이너 안에서 실행)")
        c.drawString(MARGIN + 4, 44 * mm, f"실습 저장소  https://{REPO}")
        c.setFont("Body", 8.5)
        c.setFillColor(GREY)
        c.drawString(MARGIN + 4, 28 * mm,
                     "교안의 API 응답 · 테스트 결과 · SQL 결과는 예제 코드를 실제로 실행해 얻은 것입니다.")
        c.drawString(MARGIN + 4, 22 * mm,
                     "AI 의 답변과 AI 가 만든 코드는 실행할 때마다 달라지므로, 결과 대신 확인 방법을 실었습니다.")
        c.restoreState()


# ---------------------------------------------------------------- 마크다운 → 흐름
def parse(text):
    flow = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s or re.fullmatch(r"-{3,}", s):  # 빈 줄과 가로줄(---)은 건너뛴다
            i += 1
            continue
        m_where = re.fullmatch(r"\*\*\[(PS|dev|AI|psql)\]\*\*(.*)", s)
        if s.startswith("# "):
            flow += [NextPageTemplate("body"), PageBreak(), ChapterBanner(s[2:]), Spacer(1, 10)]
        elif s.startswith("## "):
            flow += [CondPageBreak(35 * mm), Paragraph(inline(s[3:]), S["h2"])]
        elif s.startswith("### "):
            flow += [CondPageBreak(25 * mm), Paragraph(inline(s[4:]), S["h3"])]
        elif s.startswith("#### "):
            flow += [CondPageBreak(20 * mm), Paragraph(inline(s[5:]), S["h4"])]
        elif s == "@@toc":
            toc = TableOfContents()
            toc.levelStyles = [S["toc1"], S["toc2"]]
            toc.dotsMinLevel = 0
            flow.append(toc)
        elif m_where:
            # 명령을 치는 곳 표시: 색 이름표로 그리고, 아래 코드 상자와 떨어지지 않게 한다.
            color, name = WHERE[m_where.group(1)]
            rest = inline(m_where.group(2).strip())
            tag = f'<font color="{color}">■ [{m_where.group(1)}] {name}</font>'
            flow += [CondPageBreak(22 * mm),
                     Paragraph(tag + (f'&nbsp;&nbsp;<font name="Body" color="#6b7280">{rest}</font>' if rest else ""),
                               S["where"])]
        elif s.startswith("```"):
            lang = (s[3:].split() or ["text"])[0]
            buf = []
            i += 1
            while not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            # 목록 안에 들여 쓴 코드 블록은 공통 들여쓰기를 뺀다.
            indent = min((len(b) - len(b.lstrip()) for b in buf if b.strip()), default=0)
            flow += [code_table("\n".join(b[indent:] for b in buf), lang), Spacer(1, 7)]
        elif s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:])
                i += 1
            flow += quote_box(buf)
            continue
        elif s.startswith("|"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                buf.append(lines[i])
                i += 1
            flow += md_table(buf)
            continue
        elif re.match(r"^- \[[ x]\] ", s):
            flow.append(Paragraph(inline(s[6:]), S["bullet2" if line.startswith("  ") else "bullet"],
                                  bulletText="□"))
        elif s.startswith("- "):
            lvl = "bullet2" if line.startswith("  ") else "bullet"
            flow.append(Paragraph(inline(s[2:]), S[lvl], bulletText="•" if lvl == "bullet" else "–"))
        elif re.match(r"^\d+\. ", s):
            n, rest = s.split(". ", 1)
            flow.append(Paragraph(inline(rest), S["bullet"], bulletText=f"{n}."))
        else:
            para = [s]
            while (i + 1 < len(lines) and lines[i + 1].strip()
                   and not re.match(r"^(#|@@|>|```|\||- |\d+\. |-{3,}$|\*\*\[(PS|dev|AI|psql)\]\*\*)",
                                    lines[i + 1].strip())):
                i += 1
                para.append(lines[i].strip())
            flow.append(Paragraph(inline(" ".join(para)), S["body"]))
        i += 1
    return flow


# ---------------------------------------------------------------- 원고 모으기
def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def as_chapter(text, title):
    """문서의 첫 제목(# …)을 주어진 장 제목으로 바꾼다."""
    return re.sub(r"\A# .*", f"# {title}", text.lstrip(), count=1)


def demote(text, title):
    """부록에 넣을 문서: 제목을 한 단계씩 내린다. (# → ##, ## → ###, ### → ####)
    코드 상자 안의 # (주석, 예시 제목)은 건드리지 않는다."""
    out = []
    in_code = False
    first = True
    for line in text.lstrip().split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^#{1,3} ", line):
            if first and line.startswith("# "):
                line = f"## {title}"
            else:
                line = "#" + line
            first = False
        out.append(line)
    return "\n".join(out)


def manuscript():
    parts = ["# 목차\n\n@@toc\n"]
    parts.append(as_chapter(read("README.md"), "과정 안내"))
    for md in sorted((ROOT / "docs" / "lessons").glob("*.md")):
        # "다음 교시" 절은 웹에서 넘어가는 링크라서 PDF 에서는 뺀다.
        parts.append(re.sub(r"\n## 다음 교시\n.*\Z", "\n", read(md.relative_to(ROOT)), flags=re.DOTALL))

    # 부록 A: 하네스 문서 (학생이 실습에 쓰는 문서들을 그대로 싣는다)
    harness = [("# 부록 A. 하네스 문서\n\n"
               "저장소의 `harness/` 폴더에 있는 문서를 그대로 실었다. "
               "5교시부터 이 문서들을 읽고, 채우고, AI 에이전트에게 건넨다.\n")]
    for rel, title in [
        ("harness/README.md", "A-1. 하네스 폴더 안내 (harness/README.md)"),
        ("harness/REQUIREMENTS.md", "A-2. 요구사항 명세 (harness/REQUIREMENTS.md)"),
        ("harness/AGENTS.md", "A-3. 에이전트 규칙 (harness/AGENTS.md)"),
        ("harness/TASK_TEMPLATE.md", "A-4. 작업 지시서 틀 (harness/TASK_TEMPLATE.md)"),
        ("harness/tasks/06_memo_draft.md", "A-5. 6교시 작업 지시서 (harness/tasks/06_memo_draft.md)"),
        ("harness/tasks/08_db_connect.md", "A-6. 8교시 작업 지시서 (harness/tasks/08_db_connect.md)"),
        ("harness/tasks/09_update_delete.md", "A-7. 9교시 작업 지시서 (harness/tasks/09_update_delete.md)"),
        ("harness/tasks/10_web_page.md", "A-8. 10교시 작업 지시서 (harness/tasks/10_web_page.md)"),
        ("harness/tasks/11_blank_title_bug.md", "A-9. 11교시 작업 지시서 (harness/tasks/11_blank_title_bug.md)"),
        ("harness/VERIFY_CHECKLIST.md", "A-10. 검증 체크리스트 (harness/VERIFY_CHECKLIST.md)"),
        ("harness/WORKLOG.md", "A-11. 작업 기록 (harness/WORKLOG.md)"),
    ]:
        harness.append(demote(read(rel), title))
    harness.append("## A-12. 권한 규칙 (harness/opencode.jsonc)\n\n```jsonc\n"
                   + read("harness/opencode.jsonc").rstrip() + "\n```\n")
    parts.append("\n\n".join(harness))

    # 부록 B: 실행 환경 파일
    env = [("# 부록 B. 실행 환경 파일\n\n"
           "Docker 로 도구 상자를 만드는 파일과 검증 장치를 그대로 실었다. 주석을 따라 읽는다.\n")]
    for rel, lang in [("docker-compose.yml", "yaml"), ("Dockerfile", "bash"), (".env.example", "bash"),
                      ("scripts/verify.sh", "sh"), (".githooks/pre-commit", "sh"),
                      ("scripts/ask_ai.py", "python")]:
        env.append(f"## {rel}\n\n```{lang}\n{read(rel).rstrip()}\n```\n")
    parts.append("\n\n".join(env))

    # 부록 C: 완성본 코드
    code = [("# 부록 C. 완성본 코드\n\n"
            "`checkpoints/lesson11/` 의 코드다. AI 가 만든 내 코드와 똑같을 필요는 없다. "
            "같은 요구사항을 만족하는 한 가지 예로 읽는다.\n")]
    base = "checkpoints/lesson11/"
    for rel, lang in [("app/schemas.py", "python"), ("app/db.py", "python"), ("app/main.py", "python"),
                      ("app/static/index.html", "html"), ("app/static/app.js", "javascript"),
                      ("tests/conftest.py", "python"), ("tests/test_memos.py", "python")]:
        code.append(f"## {rel}\n\n```{lang}\n{read(base + rel).rstrip()}\n```\n")
    parts.append("\n\n".join(code))

    parts.append(as_chapter(read("docs/commands.md"), "부록 D. 자주 쓰는 명령 모음"))
    parts.append(as_chapter(read("docs/glossary.md"), "부록 E. 용어 풀이"))
    parts.append(as_chapter(read("docs/troubleshooting.md"), "부록 F. 오류 해결 모음"))
    return "\n\n".join(parts)


def main():
    story = [NextPageTemplate("cover"), Spacer(1, 1)] + parse(manuscript())
    OUT.parent.mkdir(exist_ok=True)
    doc = GuideDoc(OUT)
    doc.multiBuild(story)
    print("완료:", OUT, f"({doc.page}쪽)")
    if MISSING:
        print("글꼴에 없는 글자:", " ".join(sorted(MISSING)), [hex(ord(c)) for c in sorted(MISSING)])
    if len(sys.argv) > 1:  # 인자로 폴더를 주면 그곳에도 복사한다
        import shutil
        for dest in sys.argv[1:]:
            shutil.copy(OUT, Path(dest) / OUT.name)
            print("복사:", Path(dest) / OUT.name)


if __name__ == "__main__":
    main()
