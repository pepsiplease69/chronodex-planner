#!/usr/bin/env python3
"""
gen_cover.py <YEAR> <MONTH> <output.pdf>

Generates a month-at-a-glance cover page on a half-letter (5.5" × 8.5") page.
Four concentric circles divided into 31 radial segments.

Usage:
    python3 gen_cover.py 2026 3 cover_march.pdf
"""

import calendar
import math
import os

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

mm          = 2.8346
page_width  = 279.4 * mm
page_height = 215.9 * mm

_font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EuroStyle_Normal.ttf')
pdfmetrics.registerFont(TTFont('EuroStyleNormal', _font_path))
FONT = 'EuroStyleNormal'

DIAMETERS = [12.99, 11.69, 10.39, 9.09, 7.79, 6.49]
RADII     = [(d / 2) * 10 * mm for d in DIAMETERS]

DAY_LETTERS = ["M", "T", "W", "R", "F", "S", "U"]

N_SEGMENTS = 31
seg_angle  = 360.0 / N_SEGMENTS


def seg_start_angle(i):
    return -90.0 - i * seg_angle


def generate_cover(year, month, output_path):
    cx = page_width  / 2
    cy = page_height / 2

    r_outer = RADII[0]
    r_inner = RADII[-1]

    num_days   = calendar.monthrange(year, month)[1]
    month_name = calendar.month_name[month].upper()

    def pt(angle_deg, r):
        a = math.radians(angle_deg)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    c = canvas.Canvas(str(output_path), pagesize=(page_width, page_height))

    dot_spacing = 7.69 * mm
    margin      = 9.23 * mm
    x = margin
    while x <= page_width - margin:
        y = margin
        while y <= page_height - margin:
            c.setFillColorRGB(0.38, 0.38, 0.42)
            c.circle(x, y, 1.1, fill=1, stroke=0)
            y += dot_spacing
        x += dot_spacing

    c.saveState()
    c.translate(cx, cy)
    c.rotate(180)
    c.translate(-cx, -cy)

    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(1, 1, 1)
    c.circle(cx, cy, r_outer, fill=1, stroke=0)

    c.setStrokeColorRGB(0.18, 0.18, 0.20)
    c.setLineWidth(1.6)
    for r in RADII:
        c.setFillColorRGB(1, 1, 1)
        c.circle(cx, cy, r, fill=0, stroke=1)

    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(1, 1, 1)
    c.circle(cx, cy, r_inner, fill=1, stroke=0)
    c.setStrokeColorRGB(0.18, 0.18, 0.20)
    c.circle(cx, cy, r_inner, fill=0, stroke=1)

    c.setStrokeColorRGB(0.18, 0.18, 0.20)
    c.setLineWidth(1.0)
    for i in range(N_SEGMENTS):
        angle = seg_start_angle(i)
        x0, y0 = pt(angle, r_inner)
        x1, y1 = pt(angle, r_outer)
        c.line(x0, y0, x1, y1)

    r_label = (RADII[0] + RADII[1]) / 2
    label_font_size = 11.0
    c.setFont(FONT, label_font_size)
    c.setFillColorRGB(0.12, 0.12, 0.15)
    for i in range(num_days):
        angle = seg_start_angle(i) - seg_angle / 2
        lx, ly = pt(angle, r_label)
        c.saveState()
        c.translate(lx, ly)
        c.rotate(angle - 90)
        c.drawCentredString(0, -label_font_size * 0.35, str(i + 1))
        c.restoreState()

    r_day = (RADII[1] + RADII[2]) / 2
    c.setFont(FONT, label_font_size)
    c.setFillColorRGB(0.12, 0.12, 0.15)
    for i in range(num_days):
        angle   = seg_start_angle(i) - seg_angle / 2
        weekday = calendar.weekday(year, month, i + 1)
        letter  = DAY_LETTERS[weekday]
        lx, ly  = pt(angle, r_day)
        c.saveState()
        c.translate(lx, ly)
        c.rotate(angle - 90)
        c.drawCentredString(0, -label_font_size * 0.35, letter)
        c.restoreState()

    c.setFillColorRGB(0.12, 0.12, 0.15)
    c.saveState()
    c.translate(cx, cy)
    c.rotate(180)
    c.setFont(FONT, r_inner * 0.22)
    c.drawCentredString(0, r_inner * 0.12, month_name)
    c.setFont(FONT, r_inner * 0.18)
    c.drawCentredString(0, -r_inner * 0.18, str(year))
    c.restoreState()

    c.restoreState()

    c.save()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a month-at-a-glance cover page.")
    parser.add_argument("year",   type=int, help="e.g. 2026")
    parser.add_argument("month",  type=int, help="1–12")
    parser.add_argument("output", help="Output PDF path")
    args = parser.parse_args()
    generate_cover(args.year, args.month, args.output)
