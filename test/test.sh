#!/bin/sh
export PYTHONPATH="$PYTHONPATH:$HOME/workspace/NauteffVision/NauteffVision/"
echo $PYTHONPATH
python3 -m pytest 
