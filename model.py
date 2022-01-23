import math

def logistic_curve_calculate(parameters, time_value):
    baseline, asymptote, midpoint, steepness = list(parameters)
    return baseline + (asymptote-baseline)/(1 + math.exp(-steepness * (time_value - midpoint)))
