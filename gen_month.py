#!/usr/bin/env python3
"""
gen_month.py <YEAR> <MONTH>

Generates one Chronodex page per day of the given month, then merges
them all into a single PDF: output/<YEAR>-<MM>-<MonthName>.pdf

Usage:
    python3 gen_month.py 2026 3
"""

import argparse
import calendar
import os
import subprocess
import sys
from pathlib import Path

from pypdf import PdfWriter

# ── paths relative to this script ────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
DOIT_SH      = SCRIPT_DIR / "doit.sh"
PAGES_DIR    = SCRIPT_DIR / "pages"
OUTPUT_DIR   = SCRIPT_DIR / "output"

DAY_NAMES    = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
MONTH_ABBRS  = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ── CLI ───────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate a full-month Chronodex PDF.")
parser.add_argument("year",  type=int, help="e.g. 2026")
parser.add_argument("month", type=int, help="1–12")
args = parser.parse_args()

year  = args.year
month = args.month

if not (1 <= month <= 12):
    sys.exit("Month must be 1–12.")

PAGES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

month_name  = calendar.month_name[month]   # e.g. "March"
month_abbr  = MONTH_ABBRS[month]           # e.g. "Mar"
num_days    = calendar.monthrange(year, month)[1]

# ── date range: Mon of opening week → Thu of closing week ───────────────────
from datetime import date, timedelta

WORK_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday"}  # 0=Mon … 3=Thu

first_day = date(year, month, 1)
last_day  = date(year, month, num_days)

# Walk back to Monday of the first week, forward to Thursday of the last week
range_start = first_day - timedelta(days=first_day.weekday())          # Mon
range_end   = last_day  + timedelta(days=(3 - last_day.weekday()) % 7) # Thu
# If last_day is already Thu or later in the week, don't overshoot
if last_day.weekday() >= 3:   # Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    range_end = last_day + timedelta(days=max(0, 3 - last_day.weekday()))

# ── generate one page per qualifying day ─────────────────────────────────────
page_files = []
cursor = range_start
while cursor <= range_end:
    day_str  = DAY_NAMES[cursor.weekday()]

    if day_str not in WORK_DAYS:
        cursor += timedelta(days=1)
        continue

    # Label uses the actual date's month abbreviation (may differ from target month)
    day_abbr = MONTH_ABBRS[cursor.month]
    date_str = f"{day_abbr} {cursor.day}"
    out_file = PAGES_DIR / f"{cursor.year}-{cursor.month:02d}-{cursor.day:02d}.pdf"

    marker = "" if cursor.month == month else " ◂ overflow"
    print(f"  Generating {date_str} ({day_str}) → {out_file.name}{marker}")
    result = subprocess.run(
        ["fish", str(DOIT_SH), str(out_file), date_str, day_str],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(f"Error generating page for {date_str}:\n{result.stderr}")

    page_files.append(out_file)
    cursor += timedelta(days=1)

# ── merge into cumulative PDF ─────────────────────────────────────────────────
merged_path = OUTPUT_DIR / f"{year}-{month:02d}-{month_name}.pdf"
writer = PdfWriter()
for pf in page_files:
    writer.append(str(pf))

with open(merged_path, "wb") as f:
    writer.write(f)

print(f"\n✓ {len(page_files)} pages merged → {merged_path}")
