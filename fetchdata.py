import pandas

def fetch():
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

    return (omicron_cases, omicron_tests, omicron_hospital, omicron_deaths)
