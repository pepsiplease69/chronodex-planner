# ── Chronodex Planner Makefile ────────────────────────────────────────────────
#
# Targets:
#   make month  YEAR=2026 MONTH=3                     → generate full month PDF
#   make page   OUT=mar2.pdf DATE="Mar 2" DAY=Monday  → single page
#   make clean                                         → remove per-day pages/
#   make cleanall                                      → remove pages/ and output/
#
# venv activation lives in doit.sh / gen_month.fish — never here.
#
YEAR  ?= $(shell date +%Y)
MONTH ?= $(shell date +%-m)

# ── targets ───────────────────────────────────────────────────────────────────

.PHONY: month page clean cleanall help

## Generate every day of YEAR/MONTH and merge into output/
month:
	@echo "→ Generating $(YEAR)-$(MONTH) …"
	fish gen_month.fish $(YEAR) $(MONTH)

## Generate a single page: make page OUT=mar2.pdf DATE="Mar 2" DAY=Monday
page:
	@test -n "$(OUT)"  || (echo "Usage: make page OUT=mar2.pdf DATE=\"Mar 2\" DAY=Monday" && exit 1)
	@test -n "$(DATE)" || (echo "Usage: make page OUT=mar2.pdf DATE=\"Mar 2\" DAY=Monday" && exit 1)
	@test -n "$(DAY)"  || (echo "Usage: make page OUT=mar2.pdf DATE=\"Mar 2\" DAY=Monday" && exit 1)
	fish doit.sh "$(OUT)" "$(DATE)" "$(DAY)"

## Remove per-day page files
clean:
	rm -rf pages/

## Remove pages/ and output/
cleanall: clean
	rm -rf output/

## Show this help
help:
	@echo ""
	@echo "  make month  [YEAR=2026] [MONTH=3]"
	@echo "  make page   OUT=mar2.pdf DATE=\"Mar 2\" DAY=Monday"
	@echo "  make clean"
	@echo "  make cleanall"
	@echo ""
