from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math
import argparse

parser = argparse.ArgumentParser(description="Generate a Chronodex planner page.")
parser.add_argument("output_filename", help="Output PDF path, e.g. mar2.pdf")
parser.add_argument("month_date_str",  help="Date label shown in hub, e.g. \'Mar 2\'")
parser.add_argument("day_str",         help="Day label shown in hub, e.g. \'Monday\'")
args = parser.parse_args()

output_path = args.output_filename

mm = 2.8346
# US Letter Landscape: 279.4 × 215.9 mm
page_width  = 279.4 * mm
page_height = 215.9 * mm

cx_dial = page_width  / 2
cy_dial = page_height / 2

# ── FONT CONFIGURATION — swap path here when ready ───────────────────────────
# To use Arial or Eurostile, register the TTF and update FONT_REGULAR/FONT_BOLD:
#   pdfmetrics.registerFont(TTFont('Arial', '/path/to/Arial.ttf'))
#   pdfmetrics.registerFont(TTFont('Arial-Bold', '/path/to/Arial-Bold.ttf'))
#   FONT_REGULAR = 'Arial'
#   FONT_BOLD    = 'Arial-Bold'

#   pdfmetrics.registerFont(TTFont('FreeSans',     '/usr/share/fonts/truetype/freefont/FreeSans.ttf'))
#   pdfmetrics.registerFont(TTFont('FreeSansBold', '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'))
#   FONT_REGULAR = 'FreeSans'
#   FONT_BOLD    = 'FreeSansBold'

#   pdfmetrics.registerFont(TTFont('Helvetica',     '/home/alisyedz/.local/share/fonts/TTF/helvetica-255/Helvetica.ttf'))
#   pdfmetrics.registerFont(TTFont('HelveticaBold', '/home/alisyedz/.local/share/fonts/TTF/helvetica-255/Helvetica-Bold.ttf'))
#   FONT_REGULAR = 'Helvetica'
#   FONT_BOLD    = 'HelveticaBold'

import os as _os
_font_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'EuroStyle_Normal.ttf')
pdfmetrics.registerFont(TTFont('EuroStyleNormal', _font_path))
FONT_REGULAR = 'EuroStyleNormal'
FONT_BOLD    = 'EuroStyleNormal'

# ── RADII: dial diameter = page_width / 3, all proportions preserved ─────────
# In portrait the original r_large was 28mm; now we scale everything uniformly.
_r_large_orig = 28 * mm
r_large = page_width / 6          # radius = half of (page_width / 3)
_scale  = r_large / _r_large_orig  # ~1.66× — applied to every point-unit offset

r_med   = r_large * (22   / 28)
r_small = r_large * (16.5 / 28)
r_hub   = r_large * (10   / 28)

def segment_r(h):
    idx   = (h - 9) % 12
    cycle = idx % 3
    if cycle == 0: return r_small
    if cycle == 1: return r_med
    return r_large

def hr_angle(h):
    # 12 o'clock points UP  →  90° in math (counter-clockwise from +x axis)
    # Each hour = 30° clockwise = −30° in math coords
    return 90 - (h - 12) * 30

def arc_pts(cx, cy, r, a_start, a_end, steps=60):
    pts = []
    for i in range(steps + 1):
        a = math.radians(a_start + (a_end - a_start) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def draw_segment(c, cx, cy, r_inner, r_outer, a_start, a_end,
                 fill_rgb=(1,1,1), stroke_rgb=(0.18,0.18,0.2), lw=0.8):
    outer = arc_pts(cx, cy, r_outer, a_start, a_end)
    inner = arc_pts(cx, cy, r_inner, a_end, a_start)
    p = c.beginPath()
    p.moveTo(*outer[0])
    for pt in outer[1:]: p.lineTo(*pt)
    for pt in inner:     p.lineTo(*pt)
    p.close()
    c.setFillColorRGB(*fill_rgb)
    c.setStrokeColorRGB(*stroke_rgb)
    c.setLineWidth(lw)
    c.drawPath(p, fill=1, stroke=1)

def draw_tick(c, cx, cy, r_inner_t, r_outer_t, angle_deg, lw=0.25):
    a = math.radians(angle_deg)
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.setLineWidth(lw)
    c.line(cx + r_inner_t * math.cos(a), cy + r_inner_t * math.sin(a),
           cx + r_outer_t * math.cos(a), cy + r_outer_t * math.sin(a))

def draw_dial(c, cx, cy, date_str, day_str):
    main_hours = list(range(9, 21))

    for h in main_hours:
        a_start = hr_angle(h)
        a_end   = a_start - 30
        r_out   = segment_r(h)
        draw_segment(c, cx, cy, r_hub, r_out, a_start, a_end)
        tick_height = (r_out - r_hub) * 0.10
        tick_top = r_out - 1.5 * _scale
        tick_bot = tick_top - tick_height
        for frac in [0.25, 0.5, 0.75]:
            draw_tick(c, cx, cy, tick_bot, tick_top, a_start - 30 * frac)
        # Inner half-hour tick only
        inner_tick_bot = r_hub + 1.5 * _scale
        inner_tick_top = inner_tick_bot + tick_height
        draw_tick(c, cx, cy, inner_tick_bot, inner_tick_top, a_start - 15)

    # Dashed arc 9am → 11am at hub edge
    # New orientation: 9am = 270°, 11am = 210°  (clockwise from 270 to 210)
    c.setStrokeColorRGB(0.55, 0.55, 0.6)
    c.setLineWidth(0.9)
    c.setDash([4, 4])
    dash_pts = arc_pts(cx, cy, r_hub, 120, 180, steps=40)
    p = c.beginPath()
    p.moveTo(*dash_pts[0])
    for pt in dash_pts[1:]: p.lineTo(*pt)
    c.drawPath(p, fill=0, stroke=1)
    c.setDash([])

    # Hub circle
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(0.22, 0.22, 0.25)
    c.setLineWidth(1.0)
    c.circle(cx, cy, r_hub, fill=1, stroke=1)

    # ── CURVED "CHRONODEX" inside hub, 9am → 12pm arc (clockwise) ────────────
    # New orientation: 9am ≈ 270°, 12pm ≈ 180°  →  a_start=264°, a_end=186°
    text      = "CHRONODEX"
    n         = len(text)
    font_size = r_hub * 0.19
    text_r    = r_hub * 0.68
    a_start_t = 174.0
    a_end_t   = 96.0
    step      = (a_end_t - a_start_t) / (n - 1)   # negative → clockwise

    c.setFont(FONT_BOLD, font_size)
    c.setFillColorRGB(0.15, 0.15, 0.18)
    for i, ch in enumerate(text):
        ang = a_start_t + i * step
        rad = math.radians(ang)
        lx  = cx + text_r * math.cos(rad)
        ly  = cy + text_r * math.sin(rad)
        c.saveState()
        c.translate(lx, ly)
        c.rotate(ang - 90)
        c.drawCentredString(0, 0, ch)
        c.restoreState()

    # ── DATE & DAY in center of hub ──────────────────────────────────────────
    num_size = r_hub * 0.35
    c.setFont(FONT_REGULAR, num_size)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(cx, cy, date_str)
    day_size = r_hub * 0.32
    c.setFont(FONT_REGULAR, day_size)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(cx, cy - r_hub * 0.40, day_str)

    # Cardinal dots at outermost edge
    # New orientation: 12pm=left(180°), 3pm=top(90°), 6pm=right(0°), 9pm=bottom(-90°)
    for h, ang in [(12, 90), (15, 0), (18, -90), (21, 180)]:
        a  = math.radians(ang)
        dx = cx + r_large * math.cos(a)
        dy = cy + r_large * math.sin(a)
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(0.22, 0.22, 0.25)
        c.setLineWidth(1.0)
        c.circle(dx, dy, 3.5 * _scale, fill=1, stroke=1)

    # Hour labels
    c.setFont(FONT_REGULAR, 6.5 * _scale)
    for h in main_hours:
        r_out  = segment_r(h)
        r_prev = segment_r((h - 1 - 9) % 12 + 9)
        base_tip = max(r_out, r_prev) + 7 * _scale
        r_tip = r_large + 10 * _scale if h in (9, 15) else base_tip
        line_a = math.radians(hr_angle(h))
        lx = cx + r_tip * math.cos(line_a)
        ly = cy + r_tip * math.sin(line_a) - 2.5
        if h < 12:
            lbl = f"{h}am"
        elif h == 12:
            lbl = "12pm"
        elif h >= 18:
            lbl = f"{h-12}am"
        else:
            lbl = f"{h-12}pm"
        c.setFillColorRGB(0.12, 0.12, 0.15)
        c.drawCentredString(lx, ly, lbl)

def draw_dot_grid(c, x0, y0, x1, y1):
    dot_spacing = 5 * mm
    margin = 8 * mm
    x = x0 + margin
    while x <= x1 - margin:
        y = y0 + margin
        while y <= y1 - margin:
            c.setFillColorRGB(0.38, 0.38, 0.42)
            c.circle(x, y, 0.55, fill=1, stroke=0)
            y += dot_spacing
        x += dot_spacing

# ── RENDER ────────────────────────────────────────────────────────────────────
c = canvas.Canvas(output_path, pagesize=(page_width, page_height))

draw_dot_grid(c, 0, 0, page_width, page_height)
draw_dial(c, cx_dial, cy_dial, args.month_date_str, args.day_str)

c.save()
print("Saved:", output_path)
