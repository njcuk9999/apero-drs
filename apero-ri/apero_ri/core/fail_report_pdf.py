#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Fail-report PDF rendering (reportlab).

``build_fail_report_pdf`` turns the assembled report data (see
``processing_logs_api_helpers._build_fail_report_data``) into a PDF byte
string. Error lines are rendered in red on a black "code box" to match the
in-app log viewer.
"""
from __future__ import annotations

from html import escape
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


__NAME__ = "apero_ri.core.fail_report_pdf"

# Palette.
_BG_BLACK = colors.HexColor("#0b0b0b")
_ERR_RED = colors.HexColor("#ff5555")
_HEAD_BLUE = colors.HexColor("#1d4ed8")
_MUTED = colors.HexColor("#555555")
_BORDER = colors.HexColor("#cccccc")


def _styles() -> Dict[str, ParagraphStyle]:
    """Build the paragraph styles used throughout the report."""
    base = getSampleStyleSheet()
    out: Dict[str, ParagraphStyle] = dict()
    out["title"] = ParagraphStyle(
        "frTitle", parent=base["Title"], fontSize=18, spaceAfter=6,
        textColor=colors.HexColor("#111111"),
    )
    out["h2"] = ParagraphStyle(
        "frH2", parent=base["Heading2"], fontSize=13, spaceBefore=12,
        spaceAfter=4, textColor=_HEAD_BLUE,
    )
    out["h3"] = ParagraphStyle(
        "frH3", parent=base["Heading3"], fontSize=11.5, spaceBefore=8,
        spaceAfter=2, textColor=colors.HexColor("#111111"),
    )
    out["body"] = ParagraphStyle(
        "frBody", parent=base["BodyText"], fontSize=9.5, leading=13,
        alignment=TA_LEFT,
    )
    out["meta"] = ParagraphStyle(
        "frMeta", parent=base["BodyText"], fontSize=9, leading=13,
        textColor=_MUTED,
    )
    out["mono"] = ParagraphStyle(
        "frMono", parent=base["Code"], fontName="Courier", fontSize=8.5,
        leading=11, textColor=colors.HexColor("#111111"),
    )
    out["err"] = ParagraphStyle(
        "frErr", parent=base["Code"], fontName="Courier", fontSize=8,
        leading=10.5, textColor=_ERR_RED, backColor=_BG_BLACK,
        leftIndent=4, rightIndent=4, spaceBefore=0, spaceAfter=0,
    )
    out["link"] = ParagraphStyle(
        "frLink", parent=base["BodyText"], fontSize=9, leading=12,
        textColor=_HEAD_BLUE,
    )
    return out


def _kv_table(rows: List[List[Any]], styles) -> Table:
    """Build a 2-column key/value table for the summary block."""
    data = []
    for key, val in rows:
        data.append([
            Paragraph(f"<b>{escape(str(key))}</b>", styles["meta"]),
            val if isinstance(val, Paragraph)
            else Paragraph(escape(str(val)), styles["body"]),
        ])
    tbl = Table(data, colWidths=[42 * mm, 130 * mm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tbl


def _error_box(error_lines: List[str], styles) -> List[Any]:
    """Render error lines as red-on-black monospace paragraphs in a box."""
    inner = []
    for line in error_lines or []:
        safe = escape(str(line)).replace(" ", "&nbsp;")
        inner.append(Paragraph(safe or "&nbsp;", styles["err"]))
    if not inner:
        inner.append(Paragraph("(no error lines captured)", styles["err"]))
    box = Table([[inner]], colWidths=[172 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _BG_BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [box]


def build_fail_report_pdf(data: Dict[str, Any]) -> bytes:
    """Render the fail-report PDF and return its bytes.

    :param data: assembled report data with keys ``profile_id``, ``pid``,
                 ``start_time``, ``end_time``, ``total_time``, ``n_failed``,
                 ``n_passed``, ``processing_log``, ``page_url``,
                 ``error_groups`` and ``failed_recipes``.
    :return: PDF file content as bytes.
    """
    import io

    styles = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="Processing logs %s" % data.get("profile_id", ""),
    )
    story: List[Any] = []

    # ── Title + summary ────────────────────────────────────────────────
    story.append(Paragraph(
        "Processing logs %s" % escape(str(data.get("profile_id", ""))),
        styles["title"],
    ))
    page_url = str(data.get("page_url", "") or "")
    url_para = Paragraph(
        '<a href="%s" color="#1d4ed8">%s</a>' % (escape(page_url),
                                                 escape(page_url)),
        styles["link"],
    ) if page_url else Paragraph("n/a", styles["body"])

    summary_rows = [
        ["APERO group", str(data.get("pid", ""))],
        ["Start time", str(data.get("start_time", "") or "n/a")],
        ["End time", str(data.get("end_time", "") or "n/a")],
        ["Total time taken", str(data.get("total_time", "") or "n/a")],
        ["Recipes failed", str(data.get("n_failed", 0))],
        ["Recipes passed", str(data.get("n_passed", 0))],
        ["Processing log", str(data.get("processing_log", "") or "n/a")],
        ["Page", url_para],
    ]
    story.append(_kv_table(summary_rows, styles))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.6, color=_BORDER))

    # ── Error analyser ─────────────────────────────────────────────────
    error_groups = data.get("error_groups", []) or []
    story.append(Paragraph("Error analyser", styles["h2"]))
    if not error_groups:
        story.append(Paragraph(
            "No grouped errors found.", styles["body"]))
    else:
        story.append(Paragraph(
            "Similar error messages grouped together "
            "(%d group(s))." % len(error_groups), styles["meta"]))
        story.append(Spacer(1, 4))
        head = [
            Paragraph("<b>#</b>", styles["meta"]),
            Paragraph("<b>Count</b>", styles["meta"]),
            Paragraph("<b>Recipes</b>", styles["meta"]),
            Paragraph("<b>Representative error</b>", styles["meta"]),
        ]
        table_data = [head]
        for idx, grp in enumerate(error_groups, start=1):
            from apero_ri.core.fail_report import build_display_template
            raw_template = str(grp.get("template") or grp.get("message", ""))
            var_unique = grp.get("var_unique") or {}
            display_tmpl, varying_vars = build_display_template(
                raw_template, var_unique)
            # Build a single Paragraph with <br/> — reportlab table cells
            # do not reliably render a Python list of Paragraph objects.
            cell_html = escape(display_tmpl)
            for k in sorted(varying_vars, key=lambda x: int(x)
                            if x.isdigit() else 0):
                vals = varying_vars[k] or []
                val_text = ", ".join(escape(v) for v in vals)
                cell_html += "<br/><b>{{%s}}</b> → %s" % (k, val_text)
            table_data.append([
                Paragraph(str(idx), styles["meta"]),
                Paragraph(str(grp.get("count", 0)), styles["meta"]),
                Paragraph(str(grp.get("recipe_count", 0)), styles["meta"]),
                Paragraph(cell_html, styles["mono"]),
            ])
        tbl = Table(
            table_data,
            colWidths=[10 * mm, 16 * mm, 18 * mm, 128 * mm],
            repeatRows=1,
        )
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2ff")),
            ("GRID", (0, 0), (-1, -1), 0.4, _BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)

    # ── Per-error-group sections ───────────────────────────────────────
    story.append(Paragraph("Error groups", styles["h2"]))
    if not error_groups:
        story.append(Paragraph(
            "No failed recipes found for this group.", styles["body"]))

    for grp_idx, grp in enumerate(error_groups, start=1):
        from apero_ri.core.fail_report import build_display_template
        raw_template = str(grp.get("template") or grp.get("message", ""))
        var_unique = grp.get("var_unique") or {}
        display_tmpl, varying_vars = build_display_template(
            raw_template, var_unique)

        # Section heading: "Group N — <first 80 chars of template>"
        short = display_tmpl[:80] + ("…" if len(display_tmpl) > 80 else "")
        block: List[Any] = []
        block.append(Paragraph(
            "Group %d — %s" % (grp_idx, escape(short)),
            styles["h3"],
        ))

        # Summary row: count + recipe count
        block.append(_kv_table([
            ["Occurrences", str(grp.get("count", 0))],
            ["Recipes affected", str(grp.get("recipe_count", 0))],
        ], styles))

        # Full template + varying variable breakdown
        block.append(Spacer(1, 3))
        block.append(Paragraph("<b>Error template</b>", styles["meta"]))
        tmpl_box = Table(
            [[Paragraph(escape(display_tmpl), styles["mono"])]],
            colWidths=[172 * mm])
        tmpl_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f6f8")),
            ("BOX", (0, 0), (-1, -1), 0.4, _BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        block.append(tmpl_box)

        if varying_vars:
            block.append(Spacer(1, 2))
            for k in sorted(varying_vars, key=lambda x: int(x)
                            if x.isdigit() else 0):
                vals = varying_vars[k] or []
                block.append(Paragraph(
                    "<b>{{%s}}</b> → %s" % (
                        k, ", ".join(escape(v) for v in vals)),
                    styles["meta"],
                ))

        # Recipe sub-sections (one per affected recipe)
        recipe_details = grp.get("recipe_details") or []
        n_rec = len(recipe_details)
        if recipe_details:
            block.append(Spacer(1, 4))
            block.append(Paragraph(
                "<b>Affected recipes (%d)</b>" % n_rec, styles["meta"]))
            for rec_idx, rd in enumerate(recipe_details, start=1):
                recipe_name = str(rd.get("recipe_name", "") or "unknown")
                call = str(rd.get("recipe_call", "") or "")
                log_url = str(rd.get("log_url", "") or "")
                log_name = str(rd.get("log_name", "") or "")
                time_taken = str(rd.get("time_taken", "") or "n/a")

                # One unified card per recipe: dark-blue header row + light body.
                header_style = ParagraphStyle(
                    "recH%d" % rec_idx,
                    parent=styles["meta"],
                    textColor=colors.white,
                    fontName="Helvetica-Bold",
                )
                header_para = Paragraph(
                    "Recipe  <b>%s</b>   %d / %d" % (
                        escape(recipe_name), rec_idx, n_rec),
                    header_style,
                )

                # Body: call (monospace) + log link + time, all in one cell.
                body_lines = []
                if call:
                    body_lines.append(escape(call))
                if log_url and log_name:
                    body_lines.append(
                        '<a href="%s" color="#1d4ed8">%s</a>'
                        '  <font color="#6b7280">(%s)</font>' % (
                            escape(log_url), escape(log_name),
                            escape(time_taken))
                    )
                elif log_name:
                    body_lines.append(
                        "%s  <font color=\"#6b7280\">(%s)</font>" % (
                            escape(log_name), escape(time_taken))
                    )
                body_para = Paragraph(
                    "<br/>".join(body_lines) if body_lines else "(no details)",
                    styles["mono"],
                )

                rec_card = Table(
                    [[header_para], [body_para]],
                    colWidths=[172 * mm],
                )
                rec_card.setStyle(TableStyle([
                    # Header row: dark blue
                    ("BACKGROUND", (0, 0), (0, 0),
                     colors.HexColor("#1d4ed8")),
                    # Body row: very light blue
                    ("BACKGROUND", (0, 1), (0, 1),
                     colors.HexColor("#f0f4ff")),
                    ("BOX", (0, 0), (-1, -1), 0.5,
                     colors.HexColor("#93c5fd")),
                    ("LINEBELOW", (0, 0), (0, 0), 0.5,
                     colors.HexColor("#93c5fd")),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
                    ("TOPPADDING",    (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                block.append(Spacer(1, 3))
                block.append(rec_card)

        # Representative example error block
        example_lines = grp.get("block_lines") or []
        if example_lines:
            block.append(Spacer(1, 3))
            block.append(Paragraph(
                "<b>Example error</b>", styles["meta"]))
            block.extend(_error_box(example_lines, styles))

        block.append(Spacer(1, 10))
        story.append(KeepTogether(block[:3]))
        story.extend(block[3:])

    doc.build(story)
    return buf.getvalue()
