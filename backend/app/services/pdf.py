from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

FONT_PATHS = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
)
BOLD_FONT_PATHS = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
)


def build_document_pdf(*, title: str, content: str, disclaimer: str) -> bytes:
    _register_fonts()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=22 * mm,
        leftMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=title,
        author="UzbekMentorAI",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocumentTitle",
        parent=styles["Title"],
        fontName="DejaVuSans-Bold",
        fontSize=15,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.HexColor("#14213D"),
    )
    body_style = ParagraphStyle(
        "DocumentBody",
        parent=styles["BodyText"],
        fontName="DejaVuSans",
        fontSize=10.5,
        leading=16,
        spaceAfter=8,
        textColor=colors.HexColor("#202A36"),
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=body_style,
        borderColor=colors.HexColor("#D8A73F"),
        borderWidth=0.7,
        borderPadding=9,
        backColor=colors.HexColor("#FFF8E8"),
        textColor=colors.HexColor("#6B4E16"),
        spaceBefore=14,
    )

    story = [Paragraph(escape(title), title_style)]
    for block in _content_blocks(content):
        story.append(Paragraph(_format_block(block), body_style))
        story.append(Spacer(1, 2 * mm))

    story.append(Paragraph(f"<b>Ogohlantirish:</b> {escape(disclaimer)}", disclaimer_style))
    document.build(story)
    return buffer.getvalue()


def _register_fonts() -> None:
    if "DejaVuSans" in pdfmetrics.getRegisteredFontNames():
        return

    font_path = next((path for path in FONT_PATHS if path.exists()), None)
    bold_font_path = next((path for path in BOLD_FONT_PATHS if path.exists()), None)
    if font_path is None or bold_font_path is None:
        raise RuntimeError("PDF uchun DejaVu shriftlari topilmadi.")

    pdfmetrics.registerFont(TTFont("DejaVuSans", str(font_path)))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(bold_font_path)))


def _content_blocks(content: str) -> list[str]:
    return [block.strip() for block in content.replace("\r\n", "\n").split("\n\n") if block.strip()]


def _format_block(block: str) -> str:
    lines = [escape(line.strip()) for line in block.splitlines() if line.strip()]
    if not lines:
        return ""

    first = lines[0].lstrip("# ").strip()
    if lines[0].startswith("#") or (len(lines) == 1 and first.isupper()):
        return f"<b>{first}</b>"
    return "<br/>".join(lines)

