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
  if day[-1] == "1":
    day += "st"
  elif day[-1] == "2":
    day += "nd"
  elif day[-1] == "3":
    day += "rd"
  else:
    day += "th"
  weekday = d.strftime("%A")
  month = d.strftime("%B")
  year = d.strftime("%Y")
  return f"{weekday} {day} {month} {year}"

infection_saturation = get_latest('infection', 'Saturation Date')  
hospital_saturation = get_latest('hospitalisation', 'Saturation Date')
icu_saturation = get_latest('icu', 'Saturation Date')

today = time.strftime("%Y-%m-%d")

with open('output/README.md', 'w') as markdown:
  markdown.write(f"""# NSW Covid Update for {today}

This report is available in several formats:

- [NSW Covid Report {today} PDF Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/{today}/nsw-covid-report-{today}.pdf)

- [NSW Covid Report {today} Word Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/{today}/nsw-covid-report-{today}.docx)

- [Online web page](https://github.com/solresol/yet-another-pandemic-prediction/tree/main/output/README.md) (always up-to-date)


## Hospitalisation

{'Hospitals will not be saturated in the foreseeable future.' if hospital_saturation is None else 'Hospitals will be saturated on **' + format_date_nicely(hospital_saturation) + '**.'}

![]({today}/hospitalisation.png)

## ICU

{'ICU beds will continue to be available for the foreseeable future.' if icu_saturation is None else 'Every ICU bed will be occupied on on **' + format_date_nicely(icu_saturation) + '**.'}


![]({today}/icu.png)

## Number of people on ventilators

![]({today}/ventilators.png)

## Number of confirmed infections

{'It is not possible to predict accurately when the current outbreak will peak. It is too far in the future.' if infection_saturation is None else 'The current outbreak of Covid will peak on **' + format_date_nicely(infection_saturation) + '**.'}

![]({today}/infection.png)

## Deaths

![]({today}/deaths.png)


# What could be wrong with this model?

- Maybe unvaccinated people are catching Omicron first, and then having the worst outcomes, and going to hospital. So maybe once Omicron has churned through them, the number of hospital places will stop rising.

- Maybe there are vastly more cases than have been reported (e.g. people who took a RAT test and then stayed home until they recovered without telling anyone and without taking a PCR test); so maybe Omicron will saturate the population sooner than my model predicts and so we'll never get to filling the hospitals.

- Maybe the booster doses will have an unexpected effect on the number of people in hospitals, etc. That is, if the booster makes you 8 times less likely to need to go to hospital, then that just delays the date when the hospitals are overloaded by 3 weeks. But if the booster dose has super powers (1000 times less likely to need to go to hospital), then we might never saturate.

- I'm calculating everything independently of each other (hospitalisations aren't modelled as having a relationship to the number of cases). The further out you go the less accurate it is. Perhaps my inaccuracies are piling up so that even predicting 7 weeks into the future is wrong.

# How trustworthy is this?

Here are some charts of how my predictions have changed over time.

A flat line means that I have been quite consistent. A line trending down means that the situation
has been getting worse, and I have been too optimistic.

## Hospitalisation

![]({today}/historical/hospitalisation.png)

## ICU

![]({today}/historical/icu.png)

## Number of people on ventilators

![]({today}/historical/ventilators.png)

## Number of confirmed infections

![]({today}/historical/infection.png)

## Deaths

![]({today}/historical/deaths.png)

""")


os.makedirs(f'output/{today}/historical', exist_ok=True)
for history in ['deaths', 'hospitalisation', 'icu', 'infection', 'ventilators']:
  with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(8,6))
    csv = getattr(h, history)
    csv['Doubling Rate'].plot(ax=ax)
    ax.set_title(f"Predictions of the {history} doubling rate over time")
    ax.set_ylim(0, csv['Doubling Rate'].max() * 1.1)
    ax.set_ylabel(f"I said that the {history} rate appears to be doubling every _ number of days")
    ax.set_xlabel("When I made that prediction")
    fig.tight_layout()
    fig.savefig(f'output/{today}/historical/{history}.png')
