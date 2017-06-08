#!/bin/bash
tmux new-session -d -s matrix_main 'python3 main.py --set-arduino-port=/dev/ttyAMA0 --rotation=270' 