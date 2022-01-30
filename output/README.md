# NSW Covid Update for 2022-01-31

This report is available in several formats:

- [NSW Covid Report 2022-01-31 PDF Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/2022-01-31/nsw-covid-report-2022-01-31.pdf)

- [NSW Covid Report 2022-01-31 Word Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/2022-01-31/nsw-covid-report-2022-01-31.docx)

- [Online web page](https://github.com/solresol/yet-another-pandemic-prediction/tree/main/output/README.md) (always up-to-date)

## Deaths

Predictions:

| When | Total Deaths | Deaths that Day |
| ---- | ------------ | --------------- |
| Tuesday 1st February 2022 | 1432 | 34 |
| Monday 7th February 2022 | 1600 | 22 |
| Wednesday 2nd March 2022 | 1786 | 1 |

The death rate peaked on **Wednesday 26th January 2022**.

The final number of deaths (long-term) will
be close to **1797**.

![](2022-01-31/deaths.png)



## Hospitalisation

This model isn't smart enough to realise that people get better and leave the hospital.
So it ends up predicting a flat line instead of dropping back down to zero.

The number of people going into hospital peaked on **Wednesday 5th January 2022**.

![](2022-01-31/hospitalisation.png)

## ICU

This model isn't smart enough to realise that people eventually leave the ICU
(either by dying or recovering).
So it ends up predicting a flat line instead of dropping back down to zero.

The number of people going into ICU peaked on **Tuesday 4th January 2022**.

![](2022-01-31/icu.png)

## Number of people on ventilators

This model isn't smart enough to realise that people only need ventilators for
a short time (either they recover or they die). So it ends up predicting a flat line.

The number of people needing ventilators peaked on **Saturday 8th January 2022**.

![](2022-01-31/ventilators.png)

## Number of confirmed infections

Predictions:

| When | Total Infections | Infections that day |
| ---- | ------------ | --------------- |
| Tuesday 1st February 2022 | 1120150 | 7555 |
| Monday 7th February 2022 | 1147710 | 3012 |
| Monday 14th February 2022 | 1159464 | 987 |
| Wednesday 2nd March 2022 | 1164672 | 73 |

The final number of infections (long-term) will
be close to **1165091**.


According to the model, the number of people getting infected each day peaked on **Thursday 13th January 2022**. This is a smoothed-out version of reality.

Note that the first chart (showing the population) is a *log* scale chart. Going up by one line in the chart means 10 times as many people have been infected. 

It is possible that there are vastly more cases than have been
reported (e.g. people who took a RAT test and then stayed home until
they recovered without telling anyone and without taking a PCR test);
it is also possible that people aren't testing (because they can't get
RAT tests and because of the disincentives to testing) and so the
numbers here are lower than reality.


![](2022-01-31/infection.png)



# What could be wrong with this model?

- The hospitalisation, ICU and ventilator models all regress a logistic curve. They
should regress a curve that returns back down to zero.

- I'm calculating everything independently of each other (hospitalisations aren't modelled as having a relationship to the number of cases). The further out you go the less accurate it is. Perhaps my inaccuracies are piling up so that even predicting 7 weeks into the future is wrong.

