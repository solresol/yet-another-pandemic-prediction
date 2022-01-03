#!/usr/bin/env python3

import pandas
import matplotlib.pyplot
import sklearn.linear_model
import math
import numpy
import argparse
import os
import fetchdata

parser = argparse.ArgumentParser()
parser.add_argument("--copy-to", help="Output the image into another directory as well")
args = parser.parse_args()

omicron_cases, omicron_tests, omicron_hospital, omicron_deaths = fetchdata.fetch()

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



fig, axes = matplotlib.pyplot.subplots(nrows=5, figsize=(12,20))
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
if args.copy_to is not None:
   filename = os.path.join(args.copy_to, f"{date_of_prediction}.png")
   fig.savefig(filename)

filename = os.path.join('output', f"{date_of_prediction}.png")
fig.savefig(filename)
