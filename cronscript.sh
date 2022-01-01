#!/bin/sh

cd $(dirname $0)
git pull
mkdir -p output
./projection.py $*
git add output/*.png
git commit -m"Output as of $(date +%Y-%B-%d)"
