#!/bin/bash

PYTHON=.venv/bin/python

if [ ! -f $PYTHON ]
then
    make build
fi

$PYTHON main.py $@
echo "Done!"
