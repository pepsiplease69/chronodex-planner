#!/usr/bin/env fish

echo $SHELL
#python -m venv ./.venv
#pip3 install -r requirements.txt
source ../.venv/bin/activate.fish
python3 chronodex_letter.py $argv[1] $argv[2] $argv[3]
