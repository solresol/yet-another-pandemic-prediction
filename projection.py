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

def denoise_and_extrapolate(dataset, model, number_of_days=90):
    time_data = pandas.DataFrame({'when': dataset.index})
    time_data['when_tstamp'] = time_data.when.view('int64') / 1e9 / 86400
    future = pandas.DataFrame({'when':
                           [time_data.when.max() + pandas.to_timedelta(f'{n}d') for n in range(1,number_of_days)]})
    future['when_tstamp'] = future.when.view('int64') / 1e9/ 86400
    model_test = pandas.Series(data=model.predict(time_data[['when_tstamp']]),
                                index=time_data.when).map(lambda x: 10**x)
    model_extrapolate = pandas.Series(data=model.predict(future[['when_tstamp']]),
                                   index=future.when).map(lambda x: 10**x)
    return model_test, model_extrapolate

def doubling_period_of_model(model):
    return math.log10(2) / model.coef_[0]

def make_exponential_plot(dataset, title, ax, log_plot=True):
    dataset.plot(logy=log_plot, ax=ax, label=f"Actual (most recent data from {dataset.index.date.max()})")
    model = make_model(dataset)
    model_test, model_extrapolate = denoise_and_extrapolate(dataset, model)
    model_test.plot(logy=log_plot, ax=ax, color="cyan", linestyle="--", label="Model")
    model_extrapolate.plot(logy=log_plot, ax=ax, color="green", linestyle=":", label="Predicted")
    doubling_period = doubling_period_of_model(model)
    second_line_of_text = f"Doubles every {doubling_period:.1f} days"
    ax.set_title(title + "\n" + second_line_of_text)
    ax.legend(loc='lower right')


h = datamgmt.History()

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(12,5))
    dataset = omicron_cases.CASES/1e6
    make_exponential_plot(dataset, "Number of people who have been infected in NSW (millions)", ax, log_plot=False)
    ax.axhline(8.16, color="red")
    ax.annotate(xy=(time_data.when.min(), 7.8), s="Population of NSW", color='red')
    model = make_model(dataset)
    h.add_doubling_rate_to_history('infection', today, doubling_period_of_model(model))
    fig.savefig(f"output/{today}/infection.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(12,5))
    dataset = omicron_hospital.HOSP
    make_exponential_plot(dataset, "Number of covid-19 patients in hospital (log scale)", ax=ax)
    ax.axhline(20000, color="red")
    ax.annotate(xy=(time_data.when.min(), 22000), s="Number of hospital beds in NSW", color='red')
    model = make_model(dataset)
    h.add_doubling_rate_to_history('hospitalisation', today, doubling_period_of_model(model))
    fig.savefig(f"output/{today}/hospitalisation.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(12,5))
    dataset = omicron_hospital.ICU
    make_exponential_plot(dataset, "Number of covid-19 patients in ICU (log scale)",  ax=ax)
    ax.axhline(500, color='red')
    ax.axhline(2000, color='red')
    ax.annotate(xy=(time_data.when.min(),550), s="Basic ICU capacity", color='red')
    ax.annotate(xy=(time_data.when.min(),2050), s="Maximum ICU capacity (surge)", color='red')
    model = make_model(dataset)
    h.add_doubling_rate_to_history('icu', today, doubling_period_of_model(model))
    fig.savefig(f"output/{today}/icu.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(12,5))
    dataset = omicron_hospital.VENT
    make_exponential_plot(dataset, "Number of covid-19 patients on ventilators", ax=ax, log_plot=False)
    model = make_model(dataset)
    h.add_doubling_rate_to_history('ventilators', today, doubling_period_of_model(model))
    fig.savefig(f"output/{today}/ventilators.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(12,5))
    dataset = omicron_deaths.DEATHS
    make_exponential_plot(dataset, "Number of covid-19 related deaths", ax=ax, log_plot=False)
    ax.set_ylim(0,1000)
    model = make_model(dataset)
    h.add_doubling_rate_to_history('deaths', today, doubling_period_of_model(model))
    fig.savefig(f"output/{today}/deaths.png")
