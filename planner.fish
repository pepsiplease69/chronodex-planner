# Chronodex planner — source this file to get the `planner` command + completions
#   source /path/to/chronodex-planner/planner.fish

set -g _planner_root (dirname (realpath (status --current-filename)))
fish_add_path $_planner_root

# ── helpers ───────────────────────────────────────────────────────────────────

function __planner_no_subcmd
    not __fish_seen_subcommand_from month page clean cleanall
end

function __planner_month_wants_year
    set -l tokens (commandline -poc)
    __fish_seen_subcommand_from month
    and test (count $tokens) -eq 2
end

function __planner_month_wants_month
    set -l tokens (commandline -poc)
    __fish_seen_subcommand_from month
    and test (count $tokens) -eq 3
end

# ── subcommands ───────────────────────────────────────────────────────────────

complete -c planner -f -n __planner_no_subcmd -a month    -d 'Generate all pages for a month'
complete -c planner -f -n __planner_no_subcmd -a page     -d 'Generate a single day page'
complete -c planner -f -n __planner_no_subcmd -a clean    -d 'Remove per-day pages/'
complete -c planner -f -n __planner_no_subcmd -a cleanall -d 'Remove pages/ and output/'

# ── month args ────────────────────────────────────────────────────────────────

set -l _this_year (date +%Y)
complete -c planner -f -n __planner_month_wants_year \
    -a "$_this_year\tThis year "(math $_this_year + 1)"\tNext year"

complete -c planner -f -n __planner_month_wants_month -a "1\tJanuary"
complete -c planner -f -n __planner_month_wants_month -a "2\tFebruary"
complete -c planner -f -n __planner_month_wants_month -a "3\tMarch"
complete -c planner -f -n __planner_month_wants_month -a "4\tApril"
complete -c planner -f -n __planner_month_wants_month -a "5\tMay"
complete -c planner -f -n __planner_month_wants_month -a "6\tJune"
complete -c planner -f -n __planner_month_wants_month -a "7\tJuly"
complete -c planner -f -n __planner_month_wants_month -a "8\tAugust"
complete -c planner -f -n __planner_month_wants_month -a "9\tSeptember"
complete -c planner -f -n __planner_month_wants_month -a "10\tOctober"
complete -c planner -f -n __planner_month_wants_month -a "11\tNovember"
complete -c planner -f -n __planner_month_wants_month -a "12\tDecember"

# ── page flags ────────────────────────────────────────────────────────────────

complete -c planner -f -n '__fish_seen_subcommand_from page' -l out  -d 'Output PDF path'
complete -c planner -f -n '__fish_seen_subcommand_from page' -l date -d "Date label, e.g. 'Jun 15'"
complete -c planner -f -n '__fish_seen_subcommand_from page' -l day  -d 'Day of week' \
    -a 'Monday Tuesday Wednesday Thursday Friday Saturday Sunday'
