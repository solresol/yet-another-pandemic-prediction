#!/bin/sh

cd $(dirname $0)
git pull -q
mkdir -p output
./projection.py $*
git add output/*.png
TODAY=$(date +%Y-%B-%d)
git commit -q -m"Output as of $TODAY"
git push -q
