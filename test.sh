#!/bin/bash
set -eu

# Leave server window open during debug (close with C-b :kill-pane)
# tmux set-window-option remain-on-exit on
tmux new-session -c $(pwd)/ './servidor.py 51511'
tmux new-session -c $(pwd)/ './cliente.py 0.0.0.0 51511 pdf2.pdf'
./cliente.py 0.0.0.0 51511 ttLong.txt


if ! diff output/pdf2.pdf pdf2.pdf2 > /dev/null ; then
    echo "PDF failed"
    exit 1
fi

if ! diff output/ttLong.txt ttLong.txt > /dev/null ; then
    echo "ttLong failed"
    exit 1
fi

echo "All tests passed!"
rm -rf output