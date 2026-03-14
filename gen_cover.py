#!/usr/bin/env python3
"""
gen_cover.py <YEAR> <MONTH> <output.pdf>

Generates a month-at-a-glance cover page on a half-letter (5.5" × 8.5") page.
Four concentric circles divided into 31 radial segments.

Usage:
    python3 gen_cover.py 2026 3 cover_march.pdf
"""

import argparse
import calendar
import math
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── page: half letter portrait ────────────────────────────────────────────────
mm          = 2.8346
page_width  = 279.4 * mm   # 11"  (full letter landscape; print 2-up → half-letter)
page_height = 215.9 * mm   # 8.5"
cx          = page_width  / 2
cy          = page_height / 2

# ── font ─────────────────────────────────────────────────────────────────────
import os as _os
_font_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'EuroStyle_Normal.ttf')
pdfmetrics.registerFont(TTFont('EuroStyleNormal', _font_path))
FONT = 'EuroStyleNormal'

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate a month-at-a-glance cover page.")
parser.add_argument("year",   type=int, help="e.g. 2026")
parser.add_argument("month",  type=int, help="1–12")
parser.add_argument("output", help="Output PDF path")
args = parser.parse_args()

year       = args.year
month      = args.month
num_days   = calendar.monthrange(year, month)[1]
month_name = calendar.month_name[month].upper()

# ── radii (diameters: 8, 7.5, 7, 6.5 cm) ────────────────────────────────────
# outermost → innermost
DIAMETERS = [12.99, 11.69, 10.39, 9.09, 7.79, 6.49]   # cm  (all rings 8mm printed, 80mm outer)
RADII     = [(d / 2) * 10 * mm for d in DIAMETERS]   # convert cm→mm→pts
r_outer   = RADII[0]
r_inner   = RADII[-1]

# ── helpers ───────────────────────────────────────────────────────────────────
def pt(angle_deg, r):
    """Return (x, y) for a given angle (degrees, 0=right, CCW) and radius."""
    a = math.radians(angle_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)

# 31 segments: divide 360° evenly, start at top (90°) going clockwise
N_SEGMENTS = 31
seg_angle  = 360.0 / N_SEGMENTS

def seg_start_angle(i):
    """Angle of the left edge of segment i (clockwise from bottom)."""
    return -90.0 - i * seg_angle

# ── draw ──────────────────────────────────────────────────────────────────────
c = canvas.Canvas(args.output, pagesize=(page_width, page_height))

# dot grid background
dot_spacing = 10 * mm   # 5mm after 2-up print
margin      = 12 * mm   # 6mm after 2-up print
x = margin
while x <= page_width - margin:
    y = margin
    while y <= page_height - margin:
        c.setFillColorRGB(0.38, 0.38, 0.42)
        c.circle(x, y, 1.1, fill=1, stroke=0)
        y += dot_spacing
    x += dot_spacing

# ── rotate entire dial 180° around page centre ───────────────────────────────
c.saveState()
c.translate(cx, cy)
c.rotate(180)
c.translate(-cx, -cy)

# fill the annular ring white first
c.setFillColorRGB(1, 1, 1)
c.setStrokeColorRGB(1, 1, 1)
c.circle(cx, cy, r_outer, fill=1, stroke=0)

# draw the 4 concentric circles
c.setStrokeColorRGB(0.18, 0.18, 0.20)
c.setLineWidth(1.6)
for r in RADII:
    c.setFillColorRGB(1, 1, 1)
    c.circle(cx, cy, r, fill=0, stroke=1)

# fill inside innermost circle white (hub)
c.setFillColorRGB(1, 1, 1)
c.setStrokeColorRGB(1, 1, 1)
c.circle(cx, cy, r_inner, fill=1, stroke=0)
# redraw innermost ring border
c.setStrokeColorRGB(0.18, 0.18, 0.20)
c.circle(cx, cy, r_inner, fill=0, stroke=1)

# radial dividing lines: from r_inner to r_outer
c.setStrokeColorRGB(0.18, 0.18, 0.20)
c.setLineWidth(1.0)
for i in range(N_SEGMENTS):
    angle = seg_start_angle(i)
    x0, y0 = pt(angle, r_inner)
    x1, y1 = pt(angle, r_outer)
    c.line(x0, y0, x1, y1)

DAY_LETTERS  = ["M", "T", "W", "R", "F", "S", "U"]

# day numbers in outermost ring
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

# day letters in second ring
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

# month + year label in the hub — rotated 180° to read right-side up from bottom
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
print(f"Saved: {args.output}")
