from math import exp, sqrt, log
from scipy.stats import norm


class OptionsCalculator:
    @staticmethod
    def black_76(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
        """
        Calculate the price of a European call or put option using the Black-76 model.

        :param S: Current price of the underlying asset
        :param K: Strike price of the option
        :param T: Time to maturity of the option (in years)
        :param r: Risk-free interest rate
        :param sigma: Volatility of the underlying asset
        :param option_type: Type of the option ('call' or 'put')
        :return: The option price
        """
        if None in [S, K, T, r, sigma, option_type]:
            raise TypeError("None value(s) not allowed")

        if not all(isinstance(x, (int, float)) for x in
                   [S, K, T, r, sigma]) or not isinstance(option_type, str):
            raise TypeError("Inputs must be of type int or float")

        if not option_type in ["call", "put"]:
            raise ValueError("Option type must be 'call' or 'put'")

        if any(x <= 0 for x in [S, K, T, r, sigma]):
            raise ValueError("Inputs must be greater than 0")

        d1 = (log(S / K) + 0.5 * sigma ** 2 * T) / (sigma * sqrt(T))
        d2 = d1 - sigma * sqrt(T)
        if option_type == 'call':
            return exp(-r * T) * (S * norm.cdf(d1) - K * norm.cdf(d2))
        elif option_type == 'put':
            return exp(-r * T) * (K * norm.cdf(-d2) - S * norm.cdf(-d1))
        else:
            raise ValueError("Option type must be 'call' or 'put'.")

    @staticmethod
    def calculate_price(strike: float, time_to_maturity: float, risk_free_rate: float, volatility: float,
                         underlying_price: float, option_type: str) -> float:
        """
        Calculate the price of an option using the Black-76 model.

        :param strike: Strike price of the option
        :param time_to_maturity: Time to maturity of the option (in years)
        :param risk_free_rate: Risk-free interest rate
        :param volatility: Volatility of the underlying asset
        :param underlying_price: Current price of the underlying asset
        :param option_type: Type of the option ('call' or 'put')
        :return: The option price
        """
        return OptionsCalculator.black_76(underlying_price, strike, time_to_maturity, risk_free_rate, volatility,
                                          option_type)