#!/usr/bin/env python3

# This doesn't do much at the moment.

import time
import datamgmt
import matplotlib.pyplot
import os
import numpy
import pandas

h = datamgmt.History()

def get_latest(dataname, column):
  global h
  source = getattr(h, dataname)
  if column in source.columns:
    latest = source.loc[source.index.max()]
    return latest[column]
  else:
    return None

def format_date_nicely(d):
  d = pandas.to_datetime(d)
  day = d.strftime("%d")
  if day in ["11", "12", "13"]:
    day += "th"
  elif day[-1] == "1":
    day += "st"
  elif day[-1] == "2":
    day += "nd"
  elif day[-1] == "3":
    day += "rd"
  else:
    day += "th"
  if day[0] == '0':
    day = day[1:]
  weekday = d.strftime("%A")
  month = d.strftime("%B")
  year = d.strftime("%Y")
  return f"{weekday} {day} {month} {year}"

today = time.strftime("%Y-%m-%d")

with open('output/README.md', 'w') as markdown:
  markdown.write(f"""# NSW Covid Update for {today}

This report is available in several formats:

- [NSW Covid Report {today} PDF Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/{today}/nsw-covid-report-{today}.pdf)

- [NSW Covid Report {today} Word Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/{today}/nsw-covid-report-{today}.docx)

- [Online web page](https://github.com/solresol/yet-another-pandemic-prediction/tree/main/output/README.md) (always up-to-date)

## Deaths

![]({today}/deaths.png)



## Hospitalisation

This model isn't smart enough to realise that people get better and leave the hospital.
So it ends up predicting a flat line instead of dropping back down to zero.

![]({today}/hospitalisation.png)

## ICU

This model isn't smart enough to realise that people eventually leave the ICU
(either by dying or recovering).
So it ends up predicting a flat line instead of dropping back down to zero.

![]({today}/icu.png)

## Number of people on ventilators

This model isn't smart enough to realise that people only need ventilators for
a short time (either they recover or they die). So it ends up predicting a flat line.

![]({today}/ventilators.png)

## Number of confirmed infections

Note that this is a *log* scale chart. Going up by one line in the chart means
10 times as many people have been infected. It is possible that 
there are vastly more cases than have been reported (e.g. people who took a RAT test and then stayed home until they recovered without telling anyone and without taking a PCR test); so maybe Omicron will saturate the population sooner than my model predicts and so we'll never get to filling the hospitals.

![]({today}/infection.png)


# What could be wrong with this model?

- The hospitalisation, ICU and ventilator models all regress a logistic curve. They
should regress a curve that returns back down to zero.

- I'm calculating everything independently of each other (hospitalisations aren't modelled as having a relationship to the number of cases). The further out you go the less accurate it is. Perhaps my inaccuracies are piling up so that even predicting 7 weeks into the future is wrong.

""")

