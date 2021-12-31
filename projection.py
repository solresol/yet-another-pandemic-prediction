#!/usr/bin/env python3

import pandas
import matplotlib.pyplot
import sklearn.linear_model
import math
import numpy

daily_cases = pandas.read_html('https://covidlive.com.au/report/daily-cases/nsw')[1]
daily_tests = pandas.read_html('https://covidlive.com.au/report/daily-tests/nsw')[1]
daily_hospital = pandas.read_html('https://covidlive.com.au/report/daily-hospitalised/nsw')[1]
daily_deaths = pandas.read_html('https://covidlive.com.au/report/daily-deaths/nsw')[1]

daily_cases['DATE'] = pandas.to_datetime(daily_cases.DATE)
daily_tests['DATE'] = pandas.to_datetime(daily_tests.DATE)
daily_hospital['DATE'] = pandas.to_datetime(daily_hospital.DATE)
daily_deaths['DATE'] = pandas.to_datetime(daily_deaths.DATE)

daily_tests['TESTS_PERFORMED'] = daily_tests.TESTS.diff(periods=-1)

daily_cases.set_index('DATE', inplace=True)
daily_tests.set_index('DATE', inplace=True)
daily_hospital.set_index('DATE', inplace=True)
daily_deaths.set_index('DATE', inplace=True)

daily_cases.sort_index(inplace=True)
daily_tests.sort_index(inplace=True)
daily_hospital.sort_index(inplace=True)
daily_deaths.sort_index(inplace=True)

omicron_cases = daily_cases[daily_cases.index > '2021-12-01']
omicron_tests = daily_tests[daily_tests.index > '2021-12-01']
omicron_hospital = daily_hospital[daily_hospital.index > '2021-12-01']
omicron_deaths = daily_deaths[daily_deaths.index > '2021-12-01']

def make_exponential_plot(dataset, title, ax, log_plot=True):
    dataset.plot(logy=log_plot, ax=ax, label=f"Actual (most recent data from {dataset.index.date.max()})")
    log_dataset = dataset.map(math.log10)
    model = sklearn.linear_model.TheilSenRegressor()
    model.fit(time_data[['when_tstamp']], log_dataset)
    model_test = pandas.Series(data=model.predict(time_data[['when_tstamp']]), 
                                index=time_data.when).map(lambda x: 10**x)
    model_extrapolate = pandas.Series(data=model.predict(future[['when_tstamp']]), 
                                   index=future.when).map(lambda x: 10**x)
    model_test.plot(logy=log_plot, ax=ax, color="cyan", linestyle="--", label="Model")
    model_extrapolate.plot(logy=log_plot, ax=ax, color="green", linestyle=":", label="Predicted")
    doubling_period = math.log10(2) / model.coef_[0]
    second_line_of_text = f"Doubles every {doubling_period:.1f} days"
    ax.set_title(title + "\n" + second_line_of_text)
    ax.legend(loc='lower right')

time_data = pandas.DataFrame({'when': omicron_cases.index})
future = pandas.DataFrame({'when':
                           [time_data.when.max() + pandas.to_timedelta(f'{n}d') for n in range(1,90)]})
time_data['when_tstamp'] = time_data.when.view('int64') / 1e9 / 86400
future['when_tstamp'] = future.when.view('int64') / 1e9/ 86400


fig, axes = matplotlib.pyplot.subplots(nrows=5, figsize=(12,20))
#make_exponential_plot(omicron_cases.NEW, "Number of PCR tests returning positive", axes[0])
make_exponential_plot(omicron_cases.CASES/1e6, "Number of people who have been infected in NSW (millions)",
                      axes[0], log_plot=False)
axes[0].axhline(8.16, color="red")
axes[0].annotate(xy=(time_data.when.min(), 7.8), s="Population of NSW", color='red')

make_exponential_plot(omicron_hospital.HOSP, "Number of covid-19 patients in hospital (log scale)", ax=axes[1])
axes[1].axhline(20000, color="red")
axes[1].annotate(xy=(time_data.when.min(), 22000), s="Number of hospital beds in NSW", color='red')


make_exponential_plot(omicron_hospital.ICU, "Number of covid-19 patients in ICU (log scale)",  ax=axes[2])
axes[2].axhline(500, color='red')
axes[2].axhline(2000, color='red')
axes[2].annotate(xy=(time_data.when.min(),550), s="Basic ICU capacity", color='red')
axes[2].annotate(xy=(time_data.when.min(),2050), s="Maximum ICU capacity (surge)", color='red')

make_exponential_plot(omicron_hospital.VENT, "Number of covid-19 patients on ventilators", ax=axes[3], log_plot=False)

make_exponential_plot(omicron_deaths.DEATHS, "Number of covid-19 related deaths", ax=axes[4], log_plot=False)
axes[4].set_ylim(0,1000)
fig.tight_layout()
date_of_prediction = omicron_cases.index.max().date()
filename = f"/var/www/htdocs/nsw-pandemic-predictions/{date_of_prediction}.png"
fig.savefig(filename)
