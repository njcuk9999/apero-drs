#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Printable selected-period user statistics without browser rendering."""
from html import escape
from io import BytesIO
from typing import Any

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table
from reportlab.platypus import TableStyle

from apero_ri.base import base


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.core.user_statistics_pdf'
__version__ = base.__version__
__date__ = base.__date__
__authors__ = base.__authors__


# =============================================================================
# Define functions
# =============================================================================
def build_report(data: dict[str, Any], ui: dict[str, str]) -> bytes:
    """Render filtered KPIs, weekly bars and full country/region tables.

    :param data: Core summary enriched with registered_users.
    :param ui: Localized USER_STATISTICS labels.
    :return: Complete PDF bytes with escaped text and repeating table headers.
    """
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    story = [Paragraph(escape(ui['TITLE']), styles['Title'])]
    period = f'{data["start"]} - {data["end"]}'
    story.append(Paragraph(escape(period), styles['Normal']))
    story.append(Spacer(1, 12))
    metrics = [('USER_DAYS', 'total_user_days'),
               ('ACTIVE_USERS', 'unique_users'),
               ('REGISTERED_USERS', 'registered_users'),
               ('CALENDAR_DAYS', 'calendar_days')]
    for label, key in metrics:
        value = f'{ui[label]}: {data[key]}'
        story.append(Paragraph(escape(value), styles['Normal']))
    story.append(Spacer(1, 14))
    story.append(Paragraph(escape(ui['WEEKLY']), styles['Heading2']))
    weekly = data['weekly']
    if weekly:
        drawing = Drawing(480, 200)
        chart = VerticalBarChart()
        chart.x, chart.y, chart.width, chart.height = 36, 55, 430, 135
        chart.data = [[row['user_days'] for row in weekly]]
        stride = max(1, (len(weekly) + 7) // 8)
        chart.categoryAxis.categoryNames = [
            row['week'] if index % stride == 0 else ''
            for index, row in enumerate(weekly)]
        chart.categoryAxis.labels.angle = 35
        chart.categoryAxis.labels.fontSize = 7
        chart.valueAxis.valueMin = 0
        maximum = max(row['user_days'] for row in weekly)
        chart.valueAxis.valueMax = max(1, maximum * 1.15)
        chart.bars[0].fillColor = colors.HexColor('#238a8d')
        drawing.add(chart)
        story.append(drawing)
    for section, columns in [('COUNTRIES', ['COUNTRY', 'USERS', 'USER_DAYS']),
                              ('REGIONS', ['COUNTRY', 'REGION', 'USERS',
                                           'USER_DAYS'])]:
        story.append(Paragraph(escape(ui[section]), styles['Heading2']))
        rows = [[Paragraph(escape(ui[key]), styles['Normal'])
                 for key in columns]]
        for entry in data[section.lower()]:
            values = [str(entry.get(key.lower()) or ui['UNKNOWN'])
                      if key in ('COUNTRY', 'REGION')
                      else str(entry[key.lower()]) for key in columns]
            rows.append([Paragraph(escape(value), styles['Normal'])
                         for value in values])
        if len(rows) == 1:
            story.append(Paragraph(escape(ui['EMPTY']), styles['Normal']))
            continue
        table = Table(rows, colWidths=[480 / len(columns)] * len(columns),
                      repeatRows=1, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eff0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
        story.append(table)
    story.append(Spacer(1, 16))
    story.append(Paragraph(escape(ui['PRIVACY']), styles['Normal']))
    document = SimpleDocTemplate(buffer, pagesize=A4,
                                 title=ui['TITLE'], author='APERO RI',
                                 leftMargin=42, rightMargin=42)
    document.build(story)
    return buffer.getvalue()


# =============================================================================
# Start of code
# =============================================================================
if __name__ == '__main__':
    print('Hello World!')

# =============================================================================
# End of code
# =============================================================================