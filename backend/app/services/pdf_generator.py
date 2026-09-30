"""
PDF Report Generator using ReportLab
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
from typing import Optional
import datetime
from xml.sax.saxutils import escape as _escape


def _h(s) -> str:
    """HTML-escape user/LLM content for ReportLab Paragraph."""
    if s is None:
        return ""
    return _escape(str(s), {'"': '&quot;'})


PURPLE = colors.HexColor("#6366f1")
PURPLE_DARK = colors.HexColor("#4f46e5")
GREEN = colors.HexColor("#10b981")
RED = colors.HexColor("#ef4444")
ORANGE = colors.HexColor("#f59e0b")
DARK_BG = colors.HexColor("#0f172a")
CARD_BG = colors.HexColor("#1e293b")
TEXT_LIGHT = colors.HexColor("#e2e8f0")
TEXT_MUTED = colors.HexColor("#94a3b8")
WHITE = colors.white


def score_color(score: float) -> colors.Color:
    if score >= 75:
        return GREEN
    elif score >= 50:
        return ORANGE
    return RED


def score_hex(score: float) -> str:
    """Hex string for <font color> — hexval() returns int, not usable here."""
    if score >= 75:
        return "#10b981"
    elif score >= 50:
        return "#f59e0b"
    return "#ef4444"


def generate_pdf_report(
    user_name: str,
    user_email: str,
    resume_filename: str,
    job_description_preview: str,
    match_score: float,
    ats_score: float,
    matched_skills: list,
    missing_skills: list,
    feedback: dict,
    skill_roadmap: list,
    analysis_id: str,
) -> bytes:
    """Generate a professional PDF analysis report and return as bytes"""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
        title="Resume Analysis Report — CareerLens AI",
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=26,
        textColor=WHITE,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=TEXT_MUTED,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=PURPLE,
        spaceBefore=16,
        spaceAfter=8,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4,
        leading=15,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=4,
    )

    story = []

    # ─── Header Banner ────────────────────────────────────────
    header_data = [
        [Paragraph("CareerLens AI", title_style)],
        [Paragraph("AI-Powered Career Analysis Report", subtitle_style)],
        [Paragraph(
            f"Generated for: <b>{_h(user_name)}</b> ({_h(user_email)}) | {datetime.datetime.now().strftime('%B %d, %Y')}",
            subtitle_style
        )],
    ]
    header_table = Table(header_data, colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("ROUNDEDCORNERS", [10]),
        ("TOPPADDING", (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5 * cm))

    # ─── Score Cards ─────────────────────────────────────────
    story.append(Paragraph("Analysis Scores", section_title_style))

    score_data = [
        [
            Paragraph(
                f'<font size="32" color="{score_hex(match_score)}">'
                f'<b>{match_score:.0f}%</b></font><br/>'
                f'<font size="10" color="#64748b">Match Score</font>',
                ParagraphStyle("sc", alignment=TA_CENTER, leading=20)
            ),
            Paragraph(
                f'<font size="32" color="{score_hex(ats_score)}">'
                f'<b>{ats_score:.0f}%</b></font><br/>'
                f'<font size="10" color="#64748b">ATS Score</font>',
                ParagraphStyle("sc2", alignment=TA_CENTER, leading=20)
            ),
            Paragraph(
                f'<font size="32" color="#6366f1">'
                f'<b>{len(matched_skills)}</b></font><br/>'
                f'<font size="10" color="#64748b">Skills Matched</font>',
                ParagraphStyle("sc3", alignment=TA_CENTER, leading=20)
            ),
            Paragraph(
                f'<font size="32" color="#ef4444">'
                f'<b>{len(missing_skills)}</b></font><br/>'
                f'<font size="10" color="#64748b">Skills Missing</font>',
                ParagraphStyle("sc4", alignment=TA_CENTER, leading=20)
            ),
        ]
    ]
    score_table = Table(score_data, colWidths=[4.25 * cm] * 4)
    score_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.3 * cm))

    # ─── Overall Summary ─────────────────────────────────────
    if feedback.get("overall_summary"):
        story.append(Paragraph("Executive Summary", section_title_style))
        story.append(Paragraph(_h(feedback["overall_summary"]), body_style))

    # ─── Strengths & Weaknesses ──────────────────────────────
    if feedback.get("strengths") or feedback.get("weaknesses"):
        story.append(Paragraph("Strengths & Areas for Improvement", section_title_style))
        sw_data = [
            [
                Paragraph("✓ Strengths", ParagraphStyle("sh", fontSize=11, fontName="Helvetica-Bold", textColor=GREEN)),
                Paragraph("⚠ Weaknesses", ParagraphStyle("wh", fontSize=11, fontName="Helvetica-Bold", textColor=RED)),
            ]
        ]
        strengths_text = "<br/>".join(f"• {_h(s)}" for s in feedback.get("strengths", []))
        weaknesses_text = "<br/>".join(f"• {_h(w)}" for w in feedback.get("weaknesses", []))
        sw_data.append([
            Paragraph(strengths_text or "N/A", bullet_style),
            Paragraph(weaknesses_text or "N/A", bullet_style),
        ])
        sw_table = Table(sw_data, colWidths=[8.5 * cm, 8.5 * cm])
        sw_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0fdf4")),
            ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#fef2f2")),
            ("BOX", (0, 0), (0, -1), 1, GREEN),
            ("BOX", (1, 0), (1, -1), 1, RED),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(sw_table)

    # ─── Skills ──────────────────────────────────────────────
    story.append(Paragraph("Skills Analysis", section_title_style))
    if matched_skills:
        story.append(Paragraph(
            "<b>Matched Skills:</b> " + " • ".join(_h(s) for s in matched_skills),
            ParagraphStyle("ms", parent=body_style, textColor=GREEN)
        ))
    if missing_skills:
        story.append(Paragraph(
            "<b>Missing Skills:</b> " + " • ".join(_h(s) for s in missing_skills[:12]),
            ParagraphStyle("mis", parent=body_style, textColor=RED)
        ))

    # ─── Improvement Suggestions ─────────────────────────────
    if feedback.get("suggestions"):
        story.append(Paragraph("Improvement Suggestions", section_title_style))
        for suggestion in feedback.get("suggestions", []):
            story.append(Paragraph(
                f"<b>{_h(suggestion.get('section', 'General'))}:</b> {_h(suggestion.get('suggestion', ''))}",
                bullet_style
            ))

    # ─── Priority Action ─────────────────────────────────────
    if feedback.get("priority_action"):
        story.append(Spacer(1, 0.3 * cm))
        priority_data = [[
            Paragraph(
                f"🎯 <b>Priority Action:</b> {_h(feedback['priority_action'])}",
                ParagraphStyle("pa", parent=body_style, textColor=colors.HexColor("#92400e"))
            )
        ]]
        priority_table = Table(priority_data, colWidths=[17 * cm])
        priority_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
            ("BOX", (0, 0), (-1, -1), 1.5, ORANGE),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("ROUNDEDCORNERS", [6]),
        ]))
        story.append(priority_table)

    # ─── Skill Roadmap ────────────────────────────────────────
    if skill_roadmap:
        story.append(Paragraph("Skill Development Roadmap", section_title_style))
        roadmap_data = [["Skill", "Resource", "Est. Time", "Priority"]]
        for item in skill_roadmap[:6]:
            roadmap_data.append([
                _h(item.get("skill", "")),
                _h(item.get("resource", "")),
                _h(item.get("time", "")),
                _h(item.get("priority", "medium")).upper(),
            ])
        roadmap_table = Table(roadmap_data, colWidths=[3.5 * cm, 7 * cm, 2.5 * cm, 2.5 * cm])
        roadmap_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), WHITE]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
        ]))
        story.append(roadmap_table)

    # ─── Footer ──────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Paragraph(
        f"Report ID: {_h(analysis_id)} | Generated by CareerLens AI",
        ParagraphStyle("footer", fontSize=8, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceBefore=6)
    ))

    doc.build(story)
    return buffer.getvalue()
