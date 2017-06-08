#!/bin/bash
tmux new -s matrix_main
python3 main.py --set-arduino-port=/dev/ttyAMA0 --rotation=270 
tmux detach