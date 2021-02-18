#!/bin/bash
set -eu


P=${1:-51511}

# Leave server window open during debug (close with C-b :kill-pane)
# tmux set-window-option remain-on-exit on
rm -rf output
./cliente.py 127.0.0.1 $P pdf1.pdf & 
./cliente.py ::1 $P ttLong.txt &
./cliente.py 127.0.0.1 $P tt2Long.txt &
wait

if ! diff output/pdf1.pdf pdf1.pdf > /dev/null ; then
    echo "PDF failed"
    exit 1
fi

if ! diff output/tt2Long.txt tt2Long.txt > /dev/null ; then
    echo "PDF failed"
    exit 1
fi

if ! diff output/ttLong.txt ttLong.txt > /dev/null ; then
    echo "ttLong failed"
    exit 1
fi

echo "All tests passed!"
rm -rf output