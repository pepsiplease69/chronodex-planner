#!/usr/bin/env fish

echo $SHELL
source ../.venv/bin/activate.fish
python3 gen_month.py $argv[1] $argv[2]
