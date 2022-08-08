# NSW Covid Update for 2022-08-08

This report is available in several formats:

- [NSW Covid Report 2022-08-08 PDF Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/2022-08-08/nsw-covid-report-2022-08-08.pdf)

- [NSW Covid Report 2022-08-08 Word Format](https://github.com/solresol/yet-another-pandemic-prediction/raw/main/output/2022-08-08/nsw-covid-report-2022-08-08.docx)

- [Online web page](https://github.com/solresol/yet-another-pandemic-prediction/tree/main/output/README.md) (always up-to-date)

## Deaths

Predictions:

| When | Total Deaths | Deaths that Day |
| ---- | ------------ | --------------- |
| Tuesday 9th August 2022 | 4200 | 13 |
| Monday 15th August 2022 | 4281 | 13 |
| Wednesday 7th September 2022 | 4585 | 12 |

The death rate peaked on **Sunday 26th December 2021**.

The final number of deaths (long-term) will
be close to **9444**.

![](2022-08-08/deaths.png)



## Hospitalisation

This model isn't smart enough to realise that people get better and leave the hospital.
So it ends up predicting a flat line instead of dropping back down to zero.

The number of people going into hospital peaked on **Thursday 30th December 2021**.

![](2022-08-08/hospitalisation.png)

## ICU

This model isn't smart enough to realise that people eventually leave the ICU
(either by dying or recovering).
So it ends up predicting a flat line instead of dropping back down to zero.

The number of people going into ICU peaked on **Monday 21st March 2022**.

![](2022-08-08/icu.png)

## Number of people on ventilators

This model isn't smart enough to realise that people only need ventilators for
a short time (either they recover or they die). So it ends up predicting a flat line.

The number of people needing ventilators peaked on **Sunday 26th December 2021**.

![](2022-08-08/ventilators.png)

## Number of confirmed infections

Predictions:

| When | Total Infections | Infections that day |
| ---- | ------------ | --------------- |
| Tuesday 9th August 2022 | 3280895 | 8779 |
| Monday 15th August 2022 | 3332803 | 8560 |
| Monday 22nd August 2022 | 3391712 | 8307 |
| Wednesday 7th September 2022 | 3519829 | 7745 |

The final number of infections (long-term) will
be close to **5001552**.


According to the model, the number of people getting infected each day peaked on **Friday 22nd October 2021**. This is a smoothed-out version of reality.

Note that the first chart (showing the population) is a *log* scale chart. Going up by one line in the chart means 10 times as many people have been infected. 

It is possible that there are vastly more cases than have been
reported (e.g. people who took a RAT test and then stayed home until
they recovered without telling anyone and without taking a PCR test);
it is also possible that people aren't testing (because they can't get
RAT tests and because of the disincentives to testing) and so the
numbers here are lower than reality.


![](2022-08-08/infection.png)



# What could be wrong with this model?

- The hospitalisation, ICU and ventilator models all regress a logistic curve. They
should regress a curve that returns back down to zero.

- I'm calculating everything independently of each other (hospitalisations aren't modelled as having a relationship to the number of cases). The further out you go the less accurate it is. Perhaps my inaccuracies are piling up so that even predicting 7 weeks into the future is wrong.

