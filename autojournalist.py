#!/usr/bin/env python3

# This doesn't do much at the moment.

import time
import datamgmt
import matplotlib.pyplot
import os
import numpy
import pandas
import model

h = datamgmt.History()

def get_latest(dataname, column):
  global h
  source = getattr(h, dataname)
  if column in source.columns:
    latest = source.loc[source.index.max()]
    return latest[column]
  else:
    return None

def get_latest_model(dataname):
  baseline = get_latest(dataname, 'Baseline')
  asymptote = get_latest(dataname, 'Asymptote')
  midpoint = get_latest(dataname, 'Midpoint')
  steepness = get_latest(dataname, 'Steepness')
  return lambda x: model.logistic_curve_calculate((baseline, asymptote, midpoint, steepness), x)

def predict(dataname, days_in_the_future):
  global h
  source = getattr(h, dataname)
  m = get_latest_model(dataname)
  latest_day = source.index.max().timestamp() / 86400
  prediction_date = days_in_the_future + latest_day
  return m(prediction_date)

def get_peak_date(dataname):
  midpoint = get_latest(dataname, 'Midpoint')
  return format_date_nicely(midpoint * 86400 * 1e9)

def peak_is_in_the_future(dataname):
  midpoint = get_latest(dataname, 'Midpoint')
  midpoint_tstamp = midpoint * 86400 * 1e9
  return pandas.to_datetime(midpoint_tstamp) > pandas.to_datetime('now')

def format_future_nicely(dataname, days_in_the_future):
  global h
  source = getattr(h, dataname)
  m = get_latest_model(dataname)
  latest_day = source.index.max().timestamp() / 86400
  prediction_date = days_in_the_future + latest_day
  return format_date_nicely(prediction_date * 86400 * 1e9)

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

Predictions:

| When | Total Deaths | Deaths that Day |
| ---- | ------------ | --------------- |
| { format_future_nicely('deaths', 1)} | { int(predict('deaths', 1)) } | { int(predict('deaths', 1) - predict('deaths', 0)) } |
| { format_future_nicely('deaths', 7)} | { int(predict('deaths', 7)) } | { int(predict('deaths', 7) - predict('deaths', 6)) } |
| { format_future_nicely('deaths', 30)} | { int(predict('deaths', 30)) } | { int(predict('deaths', 30) - predict('deaths', 29)) } |

The death rate { "will peak on" if (peak_is_in_the_future('deaths')) else "peaked on" } **{ get_peak_date('deaths') }**.

The final number of deaths (long-term) will
be close to **{ int(get_latest('deaths', 'Asymptote')) }**.

![]({today}/deaths.png)



## Hospitalisation

This model isn't smart enough to realise that people get better and leave the hospital.
So it ends up predicting a flat line instead of dropping back down to zero.

The number of people going into hospital { "will peak on" if (peak_is_in_the_future('hospitalisation')) else "peaked on" } **{ get_peak_date('hospitalisation') }**.

![]({today}/hospitalisation.png)

## ICU

This model isn't smart enough to realise that people eventually leave the ICU
(either by dying or recovering).
So it ends up predicting a flat line instead of dropping back down to zero.

The number of people going into ICU { "will peak on" if (peak_is_in_the_future('icu')) else "peaked on" } **{ get_peak_date('icu') }**.

![]({today}/icu.png)

## Number of people on ventilators

This model isn't smart enough to realise that people only need ventilators for
a short time (either they recover or they die). So it ends up predicting a flat line.

The number of people needing ventilators { "will peak on" if (peak_is_in_the_future('ventilators')) else "peaked on" } **{ get_peak_date('ventilators') }**.

![]({today}/ventilators.png)

## Number of confirmed infections

Predictions:

| When | Total Infections | Infections that day |
| ---- | ------------ | --------------- |
| {format_future_nicely('infection', 1)} | { int(predict('infection', 1)) } | { int(predict('infection', 1) - predict('infection', 0)) } |
| {format_future_nicely('infection', 7)} | { int(predict('infection', 7)) } | { int(predict('infection', 7) - predict('infection', 6)) } |
| {format_future_nicely('infection', 14)} | { int(predict('infection', 14)) } | { int(predict('infection', 14) - predict('infection', 13)) } |
| {format_future_nicely('infection', 30)} | { int(predict('infection', 30)) } | { int(predict('infection', 30) - predict('infection', 29)) } |

The final number of infections (long-term) will
be close to **{ int(get_latest('infection', 'Asymptote')) }**.


According to the model, the number of people getting infected each day { "will peak on" if (peak_is_in_the_future('infection')) else "peaked on" } **{ get_peak_date('infection') }**. This is a smoothed-out version of reality.

Note that the first chart (showing the population) is a *log* scale chart. Going up by one line in the chart means 10 times as many people have been infected. 

It is possible that there are vastly more cases than have been
reported (e.g. people who took a RAT test and then stayed home until
they recovered without telling anyone and without taking a PCR test);
it is also possible that people aren't testing (because they can't get
RAT tests and because of the disincentives to testing) and so the
numbers here are lower than reality.


![]({today}/infection.png)



# What could be wrong with this model?

- The hospitalisation, ICU and ventilator models all regress a logistic curve. They
should regress a curve that returns back down to zero.

- I'm calculating everything independently of each other (hospitalisations aren't modelled as having a relationship to the number of cases). The further out you go the less accurate it is. Perhaps my inaccuracies are piling up so that even predicting 7 weeks into the future is wrong.

""")

