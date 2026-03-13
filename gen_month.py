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

# ── generate one page per day ─────────────────────────────────────────────────
page_files = []
for day in range(1, num_days + 1):
    weekday   = calendar.weekday(year, month, day)   # 0=Mon … 6=Sun
    day_str   = DAY_NAMES[weekday]
    date_str  = f"{month_abbr} {day}"
    out_file  = PAGES_DIR / f"{year}-{month:02d}-{day:02d}.pdf"

    print(f"  Generating {date_str} ({day_str}) → {out_file.name}")
    result = subprocess.run(
        ["fish", str(DOIT_SH), str(out_file), date_str, day_str],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        sys.exit(f"Error generating page for {date_str}:\n{result.stderr}")

    page_files.append(out_file)

# ── merge into cumulative PDF ─────────────────────────────────────────────────
merged_path = OUTPUT_DIR / f"{year}-{month:02d}-{month_name}.pdf"
writer = PdfWriter()
for pf in page_files:
    writer.append(str(pf))

with open(merged_path, "wb") as f:
    writer.write(f)

print(f"\n✓ {num_days} pages merged → {merged_path}")
