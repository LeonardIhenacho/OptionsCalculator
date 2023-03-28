import numpy as np
import scipy.stats as si


# Function to calculate the normal distribution for a given mean and standard deviation.
class OptionsCalculator():
    """ Calculate normal distributions for use in the black 76 formula then have different formula for call and put
    options. Formula taken from LME website located here:
    https://www.lme.com/en/trading/contract-types/options/black-scholes-76-formula """

    @staticmethod
    def NormalDist(x):
        normalDist = si.norm.cdf(x, 0.0, 1.0)
        return normalDist

    @staticmethod
    def Call(Strike, Maturity, RiskFreeRate, Volatility, FuturePrice):
        d1 = (np.log(FuturePrice / Strike) + (0.5 * Volatility ** 2) * Maturity) / (Volatility * np.sqrt(Maturity))
        d2 = (np.log(FuturePrice / Strike) - (0.5 * Volatility ** 2) * Maturity) / (Volatility * np.sqrt(Maturity))
        pv = np.exp(-RiskFreeRate * Maturity) * (FuturePrice * OptionsCalculator.NormalDist(d1) - Strike *
                                                 OptionsCalculator.NormalDist(d2))
        return pv

    @staticmethod
    def Put(Strike, Maturity, RiskFreeRate, Volatility, FuturePrice):
        d1 = (np.log(FuturePrice / Strike) + (0.5 * Volatility ** 2) * Maturity) / (Volatility * np.sqrt(Maturity))
        d2 = (np.log(FuturePrice / Strike) - (0.5 * Volatility ** 2) * Maturity) / (Volatility * np.sqrt(Maturity))
        pv = np.exp(-RiskFreeRate * Maturity) * (Strike * OptionsCalculator.NormalDist(-d2) - FuturePrice *
                                                 OptionsCalculator.NormalDist(-d1))
        return pv
