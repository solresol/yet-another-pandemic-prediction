#!/usr/bin/env python3

import pandas
import matplotlib.pyplot
from matplotlib.ticker import FuncFormatter
import sklearn.linear_model
import math
import numpy
import argparse
import os
import datamgmt
import time
import scipy
import model

today = time.strftime("%Y-%m-%d")
os.makedirs(f'output/{today}', exist_ok=True)

omicron_cases, omicron_tests, omicron_hospital, omicron_deaths = datamgmt.fetch_covidlive()

time_data = pandas.DataFrame({'when': omicron_cases.index})
time_data['when_tstamp'] = time_data.when.view('int64') / 1e9 / 86400

h = datamgmt.History()

def error_on_logistic_curve(parameters, dataset, timestamps):
    predictions = numpy.array([model.logistic_curve_calculate(parameters, t) for t in timestamps])
    return numpy.linalg.norm(predictions - dataset)

def plot_curve(dataset, timestamps, logistic_parameters, ax=None, yscale='linear', days_of_future=60):
    if ax is None:
        fig, ax = matplotlib.pyplot.subplots()
    ax.set_yscale(yscale)
    plot_points = []
    for t in timestamps.when_tstamp:
        plot_points.append(model.logistic_curve_calculate(logistic_parameters,t))
    projections = pandas.Series(data=plot_points, index=timestamps.when)
    projections.plot(ax=ax, c='red', linestyle='--', label="Model")
    extrapolation_points = []
    extrapolation_dates = []
    for extrapolation_time in numpy.arange(timestamps.when_tstamp.max(), timestamps.when_tstamp.max()+days_of_future,1.0):
        extrapolation_points.append(model.logistic_curve_calculate(logistic_parameters, extrapolation_time))
        extrapolation_dates.append(pandas.to_datetime(extrapolation_time * 86400 * 1000000000))
    extrapolation = pandas.Series(data=extrapolation_points, index=extrapolation_dates)
    extrapolation.plot(ax=ax, c='green', linestyle='--', label="Extrapolation")
    series = pandas.Series(data=list(dataset), index=timestamps.when)
    series.sort_index(inplace=True)
    series.plot(ax=ax, label="Actual")
    ax.legend()


def millions_formatter(x, pos):
    return f'{x / 1000000}'

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, axes = matplotlib.pyplot.subplots(figsize=(8,8), nrows=2)
    # millions_of_cases = omicron_cases.CASES / 1e6
    # millions_of_cases_result = scipy.optimize.minimize(
    #     error_on_logistic_curve, 
    #     [0.1,1,19000, 0.001],
    #     (millions_of_cases, time_data.when_tstamp),
    #     tol=0.1
    # )
    # plot_curve(millions_of_cases, time_data, millions_of_cases_result.x, ax=ax, yscale='log')

    omicron_cases_result = scipy.optimize.minimize(
        error_on_logistic_curve, 
        [100000,1000000,19000, 0.001],
        (omicron_cases.CASES, time_data.when_tstamp),
        tol=0.1
    )
    ax = axes[0]
    plot_curve(omicron_cases.CASES, time_data, omicron_cases_result.x, ax=ax, yscale='log')
    ax.set_title("Number of people who have been infected in NSW - log scale")
    ax.axhline(7.8*1e6, color="red")
    ax.annotate(xy=(time_data.when.min(), 6.5*1e6), s="Population of NSW", color='red')
    ax = axes[1]
    plot_curve(omicron_cases.CASES, time_data, omicron_cases_result.x, ax=ax)
    ax.set_title("Number of people who have been infected in NSW")
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax.set_ylabel("Infection count (millions)")
    h.add_logistic_parameters_to_history('infection', 'today', *omicron_cases_result.x)
    fig.tight_layout()
    fig.savefig(f"output/{today}/infection.png")
    

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(8,4))
    hospital_result = scipy.optimize.minimize(
        error_on_logistic_curve, 
        [140,3000,19000, 0.2],
        (omicron_hospital.HOSP, time_data.when_tstamp),
        tol=0.1, method='Nelder-Mead'
    )
    plot_curve(omicron_hospital.HOSP, time_data, hospital_result.x, ax=ax)
    ax.set_title("Number of covid-19 patients in hospital")
    #ax.axhline(20000, color="red")
    #ax.annotate(xy=(time_data.when.min(), 22000), s="Number of hospital beds in NSW", color='red')
    h.add_logistic_parameters_to_history('hospitalisation', 'today', *hospital_result.x)    
    fig.savefig(f"output/{today}/hospitalisation.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(8,4))
    icu_result = scipy.optimize.minimize(
        error_on_logistic_curve, 
        [25,250,19000, 0.2],
        (omicron_hospital.ICU, time_data.when_tstamp),
        tol=0.1, method='Nelder-Mead'
    )
    plot_curve(omicron_hospital.ICU, time_data, icu_result.x, ax=ax)
    ax.set_title("Number of covid-19 patients in ICU")
    ax.axhline(500, color='red')
    #ax.axhline(2000, color='red')
    ax.annotate(xy=(time_data.when.min(),450), s="Basic ICU capacity", color='red')
    #ax.annotate(xy=(time_data.when.min(),2050), s="Maximum ICU capacity (surge)", color='red')
    h.add_logistic_parameters_to_history('icu', 'today', *icu_result.x)        
    fig.savefig(f"output/{today}/icu.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(8,4))
    ventilator_result = scipy.optimize.minimize(
        error_on_logistic_curve, 
        [0,10,19000, 0.2],
        (omicron_hospital.VENT, time_data.when_tstamp),
        tol=0.1
    )
    plot_curve(omicron_hospital.VENT, time_data, ventilator_result.x, ax=ax)
    ax.set_title("Number of covid-19 patients on ventilators")
    h.add_logistic_parameters_to_history('ventilators', 'today', *ventilator_result.x)           
    fig.savefig(f"output/{today}/ventilators.png")

with matplotlib.pyplot.style.context('seaborn-darkgrid'):
    fig, ax = matplotlib.pyplot.subplots(figsize=(8,4))
    deaths_result = scipy.optimize.minimize(
        error_on_logistic_curve, 
        [635,1500,19000, 0.15],
        (omicron_deaths.DEATHS, time_data.when_tstamp),
        tol=0.1
    )
    plot_curve(omicron_deaths.DEATHS, time_data, deaths_result.x, ax=ax)
    ax.set_title("Number of covid-19 related deaths")
    h.add_logistic_parameters_to_history('deaths', 'today', *deaths_result.x)               
    fig.savefig(f"output/{today}/deaths.png")
