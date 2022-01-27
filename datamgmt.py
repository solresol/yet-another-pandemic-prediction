import pandas
import glob
import os
import time

def fetch_covidlive():
    today = time.strftime("%Y-%m-%d")
    cache = f'.temp_cache/{today}'
    if os.path.exists(cache):
        daily_cases = pandas.read_csv('{cache}/daily_cases.csv')
        daily_tests = pandas.read_csv('{cache}/daily_tests.csv')
        daily_hospital = pandas.read_csv('{cache}/daily_hospital.csv')
        daily_deaths = pandas.read_csv('{cache}/daily_deaths.csv')
    else:
        daily_cases = pandas.read_html('https://covidlive.com.au/report/daily-cases/nsw')[1]
        daily_tests = pandas.read_html('https://covidlive.com.au/report/daily-tests/nsw')[1]
        daily_hospital = pandas.read_html('https://covidlive.com.au/report/daily-hospitalised/nsw')[1]
        daily_deaths = pandas.read_html('https://covidlive.com.au/report/daily-deaths/nsw')[1]
        os.makedirs(f'.temp-cache/{today}', exist_ok=True)
        daily_cases.to_csv(f'.temp-cache/{today}/daily_cases.csv', index=False)
        daily_tests.to_csv(f'.temp-cache/{today}/daily_tests.csv', index=False)
        daily_hospital.to_csv(f'.temp-cache/{today}/daily_hospital.csv', index=False)
        daily_deaths.to_csv(f'.temp-cache/{today}/daily_deaths.csv', index=False)            

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

    omicron_cases = daily_cases[daily_cases.index >= '2021-12-01']
    omicron_tests = daily_tests[daily_tests.index >= '2021-12-01']
    #omicron_hospital = daily_hospital[daily_hospital.index > '2021-12-15']
    #omicron_deaths = daily_deaths[daily_deaths.index > '2022-01-01']
    omicron_hospital = daily_hospital[daily_hospital.index >= '2021-12-01']
    omicron_deaths = daily_deaths[daily_deaths.index >= '2021-12-01']

    return (omicron_cases, omicron_tests, omicron_hospital, omicron_deaths)


class History:
    def __init__(self):
        self.__data = {}
        for filename in glob.glob('historical/*.csv'):
            basename = os.path.basename(filename)
            data_name, csv = os.path.splitext(basename)
            self.__data[data_name] = pandas.read_csv(filename)
            self.__data[data_name]['Date'] = pandas.to_datetime(self.__data[data_name]['Date'])
            self.__data[data_name].set_index('Date', inplace=True)

    def __getattr__(self, data_name):
        return self.__data[data_name].copy()

    def add_doubling_rate_to_history(self, data_name, date, doubling_rate):
        csv = self.__data[data_name]
        # Give me your worst date format, and I'll handle it
        date = pandas.to_datetime(date)
        if date in set(csv.index):
            csv.loc[date, 'Doubling Rate'] = doubling_rate
        else:
            new_csv = pandas.DataFrame({'Doubling Rate':
                                        pandas.Series(data=[doubling_rate], index=[date])})
            self.__data[data_name] = pandas.concat([csv, new_csv])
            csv = self.__data[data_name]
            csv.sort_index(inplace=True)
            csv.index.rename('Date', inplace=True)
        csv.to_csv(f"historical/{data_name}.csv")

    def add_saturation_date_to_history(self, data_name, date, saturation_date):
        csv = self.__data[data_name]
        # Give me your worst date format, and I'll handle it
        date = pandas.to_datetime(date)
        saturation_date = pandas.to_datetime(saturation_date).strftime('%Y-%m-%d')
        if 'Saturation Date' not in csv.columns:
            csv['Saturation Date'] = None
        if date in set(csv.index):
            csv.loc[date, 'Saturation Date'] = saturation_date
        else:
            new_csv = pandas.DataFrame({'Saturation Date':
                                        pandas.Series(data=[saturation_date], index=[date])})
            self.__data[data_name] = pandas.concat([csv, new_csv])
            csv = self.__data[data_name]
            csv.sort_index(inplace=True)
            csv.index.rename('Date', inplace=True)
        csv.to_csv(f"historical/{data_name}.csv")

    def add_logistic_parameters_to_history(self, data_name, date, baseline, asymptote, midpoint, steepness):
        csv = self.__data[data_name]
        # Give me your worst date format, and I'll handle it
        date = pandas.to_datetime(date)
        if date in set(csv.index):
            csv.loc[date, 'Baseline'] = baseline
            csv.loc[date, 'Asymptote'] = asymptote
            csv.loc[date, 'Midpoint'] = midpoint
            csv.loc[date, 'Steepness'] = steepness
        else:
            new_csv = pandas.DataFrame(
                {
                    'Baseline': pandas.Series(data=[baseline], index=[date]),
                    'Asymptote': pandas.Series(data=[asymptote], index=[date]),
                    'Midpoint': pandas.Series(data=[midpoint], index=[date]),
                    'Steepness': pandas.Series(data=[steepness], index=[date])
                })
            self.__data[data_name] = pandas.concat([csv, new_csv])
            csv = self.__data[data_name]
            csv.sort_index(inplace=True)
            csv.index.rename('Date', inplace=True)
        csv.to_csv(f"historical/{data_name}.csv")
