#!/bin/sh

cd $(dirname $0)
git pull -q
mkdir -p output
./projection.py
./autojournalist.py
TODAY_WORDS=$(date +%Y-%B-%d)
TODAY=$(date +%Y-%m-%d)
(cd output ; pandoc -f markdown -t docx -o ${TODAY}/nsw-covid-report-${TODAY}.docx README.md )
(cd output ; pandoc -f markdown -t latex --toc -o ${TODAY}/nsw-covid-report-${TODAY}.pdf README.md )
git add output/${TODAY}/*.png output/${TODAY}/nsw-covid-report-${TODAY}.docx output/${TODAY}/nsw-covid-report-${TODAY}.pdf output/README.md
git commit -q -m"Output as of $TODAY_WORDS"
git add historical/*.csv
git commit -q -m"Record the predictions as of ${TODAY_WORDS}"
git push -q
