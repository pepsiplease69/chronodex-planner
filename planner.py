#!/usr/bin/env python3
"""
Chronodex Planner CLI

Usage:
    python planner.py month [YEAR] [MONTH]
    python planner.py page --out <file> --date <"Mon D"> --day <Weekday>
    python planner.py clean
    python planner.py cleanall
"""

import argparse
import shutil
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PAGES_DIR  = SCRIPT_DIR / "pages"
OUTPUT_DIR = SCRIPT_DIR / "output"


def cmd_month(args):
    from gen_month import generate_month
    generate_month(args.year, args.month)


def cmd_page(args):
    from chronodex_letter import generate_page
    generate_page(args.out, args.date, args.day)


def cmd_clean(args):
    if PAGES_DIR.exists():
        shutil.rmtree(PAGES_DIR)
        print(f"Removed {PAGES_DIR}")
    else:
        print("Nothing to clean.")


def cmd_cleanall(args):
    cmd_clean(args)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        print(f"Removed {OUTPUT_DIR}")


today = date.today()

parser = argparse.ArgumentParser(
    description="Generate Chronodex planner PDFs.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
sub = parser.add_subparsers(dest="command", required=True)

# month
p_month = sub.add_parser("month", help="Generate all pages for a month")
p_month.add_argument("year",  type=int, nargs="?", default=today.year,
                     help=f"Year (default: {today.year})")
p_month.add_argument("month", type=int, nargs="?", default=today.month,
                     help=f"Month 1–12 (default: {today.month})")
p_month.set_defaults(func=cmd_month)

# page
p_page = sub.add_parser("page", help="Generate a single day page")
p_page.add_argument("--out",  required=True, help="Output PDF path, e.g. jun15.pdf")
p_page.add_argument("--date", required=True, help="Date label for hub, e.g. 'Jun 15'")
p_page.add_argument("--day",  required=True,
                    choices=["Monday","Tuesday","Wednesday","Thursday",
                             "Friday","Saturday","Sunday"],
                    help="Day of week")
p_page.set_defaults(func=cmd_page)

# clean
p_clean = sub.add_parser("clean", help="Remove per-day pages/")
p_clean.set_defaults(func=cmd_clean)

# cleanall
p_cleanall = sub.add_parser("cleanall", help="Remove pages/ and output/")
p_cleanall.set_defaults(func=cmd_cleanall)

if __name__ == "__main__":
    args = parser.parse_args()
    args.func(args)
