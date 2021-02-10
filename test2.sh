#!/bin/bash
set -eu

P=${1:-51511}

# Leave server window open during debug (close with C-b :kill-pane)
# tmux set-window-option remain-on-exit on
rm -rf output
./cliente.py 0.0.0.0 $P emptyfile.txt 

if ! diff output/emptyfile.txt emptyfile.txt > /dev/null ; then
    echo "Empty failed"
    exit 1
fi

echo "All tests passed!"
rm -rf output