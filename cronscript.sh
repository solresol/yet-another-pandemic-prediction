#!/bin/sh

cd $(dirname $0)
git pull -q
mkdir -p output
./projection.py $*
./autojournalist.py $*
git add output/*.png output/README.md
TODAY=$(date +%Y-%B-%d)
git commit -q -m"Output as of $TODAY"
git push -q
