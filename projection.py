#!/usr/bin/env python3

import pandas
import matplotlib.pyplot
import sklearn.linear_model
import math
import numpy
import argparse
import os
import datamgmt
import time

today = time.strftime("%Y-%m-%d")
os.makedirs(f'output/{today}', exist_ok=True)

omicron_cases, omicron_tests, omicron_hospital, omicron_deaths = datamgmt.fetch_covidlive()

time_data = pandas.DataFrame({'when': omicron_cases.index})
time_data['when_tstamp'] = time_data.when.view('int64') / 1e9 / 86400

def make_model(dataset):
    time_data = pandas.DataFrame({'when': dataset.index})
    time_data['when_tstamp'] = time_data.when.view('int64') / 1e9 / 86400
    log_dataset = dataset.map(math.log10)
    model = sklearn.linear_model.TheilSenRegressor()
    model.fit(time_data[['when_tstamp']], log_dataset)
    return model

def make_future_dates(starting_date='today', number_of_days=90):
    starting_date = pandas.to_datetime(starting_date)
    future = pandas.DataFrame({'when':
                           [starting_date + pandas.to_timedelta(f'{n}d') for n in range(1,number_of_days)]})
    future['when_tstamp'] = future.when.view('int64') / 1e9/ 86400
    return future

def denoise_and_extrapolate(dataset, model, number_of_days=90, saturation_value=None):
    time_data = pandas.DataFrame({'when': dataset.index})
    time_data['when_tstamp'] = time_data.when.view('int64') / 1e9 / 86400
    model_test = pandas.Series(data=model.predict(time_data[['when_tstamp']]),
                                   index=time_data.when).map(lambda x: 10**x)
    if saturation_value is None:
        future = make_future_dates(time_data.when.max(), number_of_days)
    else:
        future = make_future_dates_until_saturation(model, saturation_value)

    model_extrapolate = pandas.Series(data=model.predict(future[['when_tstamp']]),
                                   index=future.when).map(lambda x: 10**x)
    return model_test, model_extrapolate

def doubling_period_of_model(model):
    return math.log10(2) / model.coef_[0]

def find_saturation_date(model, saturation_value, starting_date='today'):
    future = make_future_dates(starting_date)
    model_extrapolate = pandas.Series(data=model.predict(future[['when_tstamp']]),
                                      index=future.when).map(lambda x: 10**x)
    model_extrapolate = model_extrapolate[model_extrapolate > saturation_value]
    if model_extrapolate.shape[0] == 0:
        return None
    return pandas.to_datetime(model_extrapolate.idxmin().strftime('%Y-%m-%d'))

def make_future_dates_until_saturation(model, saturation_value):
    answer = make_future_dates()
    saturation_date = find_saturation_date(model, saturation_value)
    if saturation_date is None:
        return answer
    saturation_date = pandas.to_datetime(saturation_date) + pandas.to_timedelta("7d")
    answer = answer[answer.when <= saturation_date]
    return answer

def make_exponential_plot(dataset, title, ax, log_plot=True, saturation_value=None):
    model = make_model(dataset)
    model_test, model_extrapolate = denoise_and_extrapolate(dataset, model, saturation_value=saturation_value)
    model_extrapolate.plot(logy=log_plot, ax=ax, color="green", linestyle=":", label="Predicted")
    model_test.plot(logy=log_plot, ax=ax, color="cyan", linestyle="--", label="Model")
    dataset.plot(logy=log_plot, ax=ax, label=f"Actual (most recent data from {dataset.index.date.max()})")
    doubling_period = doubling_period_of_model(model)
    second_line_of_text = f"Doubles every {doubling_period:.1f} days"
    ax.set_title(title + "\n" + second_line_of_text)
    ax.legend(loc='lower right')


h = datamgmt.History()

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, axes = matplotlib.pyplot.subplots(figsize=(12,4), ncols=2)
    dataset = omicron_cases.CASES/1e6
    make_exponential_plot(dataset, "Number of people who have been infected in NSW (millions)", axes[0], log_plot=False, saturation_value=7.8)
    make_exponential_plot(dataset*1e6, "Number of people who have been infected in NSW - log plot", axes[1], log_plot=True)
    axes[0].axhline(7.8, color="red")
    axes[0].annotate(xy=(time_data.when.min(), 7.3), s="Population of NSW", color='red')
    axes[1].axhline(7800000, color="red")
    axes[1].annotate(xy=(time_data.when.min(), 6000000), s="Population of NSW", color='red')
    model = make_model(dataset)
    saturation = find_saturation_date(model, 7.8 / 3)
    # I am assuming that we can safely model an exponential until we are at a third of the saturation. After that the infection rates will drop quite quickly.
    if saturation is not None:
        h.add_saturation_date_to_history('infection', today, saturation)
    h.add_doubling_rate_to_history('infection', today, doubling_period_of_model(model))
    fig.savefig(f"output/{today}/infection.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, axes = matplotlib.pyplot.subplots(figsize=(12,4), ncols=2)
    ax = axes[0]
    dataset = omicron_hospital.HOSP
    make_exponential_plot(dataset, "Number of covid-19 patients in hospital", ax=ax, log_plot=False, saturation_value=20000)
    ax.axhline(20000, color="red")
    ax.annotate(xy=(time_data.when.min(), 22000), s="Number of hospital beds in NSW", color='red')
    model = make_model(dataset)
    saturation = find_saturation_date(model, 20000)
    if saturation is not None:
        h.add_saturation_date_to_history('hospitalisation', today, saturation)
    h.add_doubling_rate_to_history('hospitalisation', today, doubling_period_of_model(model))
    hospitals_saturated = saturation
    make_exponential_plot(dataset, "Number of covid-19 patients in hospital (log plot)", ax=axes[1], log_plot=True, saturation_value=20000)
    axes[1].axhline(20000, color="red")
    fig.savefig(f"output/{today}/hospitalisation.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, axes = matplotlib.pyplot.subplots(figsize=(12,4),ncols=2)
    ax = axes[0]
    dataset = omicron_hospital.ICU
    make_exponential_plot(dataset, "Number of covid-19 patients in ICU",  ax=ax, log_plot=False, saturation_value=2000)
    ax.axhline(500, color='red')
    ax.axhline(2000, color='red')
    ax.annotate(xy=(time_data.when.min(),550), s="Basic ICU capacity", color='red')
    ax.annotate(xy=(time_data.when.min(),2050), s="Maximum ICU capacity (surge)", color='red')
    model = make_model(dataset)
    saturation = find_saturation_date(model, 550)
    if saturation is not None:
        h.add_saturation_date_to_history('icu', today, saturation)

    h.add_doubling_rate_to_history('icu', today, doubling_period_of_model(model))

    make_exponential_plot(dataset, "Number of covid-19 patients in ICU (log plot)",  ax=axes[1], log_plot=True, saturation_value=2000)
    axes[1].axhline(500, color='red')
    axes[1].axhline(2000, color='red')

    fig.savefig(f"output/{today}/icu.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, axes = matplotlib.pyplot.subplots(figsize=(12,4), ncols=2)
    ax = axes[0]
    dataset = omicron_hospital.VENT
    make_exponential_plot(dataset, "Number of covid-19 patients on ventilators", ax=ax, log_plot=False)
    model = make_model(dataset)
    h.add_doubling_rate_to_history('ventilators', today, doubling_period_of_model(model))
    make_exponential_plot(dataset, "Number of covid-19 patients on ventilators (log plot)", ax=axes[1], log_plot=True)

    fig.savefig(f"output/{today}/ventilators.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(8,4))
    dataset = omicron_deaths.DEATHS
    make_exponential_plot(dataset, "Number of covid-19 related deaths", ax=ax, log_plot=False)
    ax.set_ylim(0,5000)
    ax.axvline(hospitals_saturated, linestyle="--", color="grey")
    ax.annotate(xy=(hospitals_saturated, 750), s="Hospital saturation date")
    model = make_model(dataset)
    h.add_doubling_rate_to_history('deaths', today, doubling_period_of_model(model))
    fig.savefig(f"output/{today}/deaths.png")
