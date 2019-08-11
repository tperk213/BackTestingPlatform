import pandas as pd
import pandas_datareader.data as web
from datetime import datetime
import statsmodels.tsa.stattools as ts
from numpy import cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
# import data as df

amzn = web.DataReader("AMZN", "yahoo", datetime(2000, 1, 1), datetime(2015, 1, 1))

# Dicky fuller test
fuller = ts.adfuller(amzn["Adj Close"], 1)

print(fuller)

# Hurst exponent


def hurst(ts):
    lags = range(2, 100)
    """
        create two series of ts and ts laged by lag
        create series of difference of two series at each point
        find std of that series
        sqrt it
        repeat for all lags to 100
        create series of these values
    """
    if type(ts) == type(pd.Series()):
        ts = ts.to_numpy()
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]

    poly = polyfit(log(lags), log(tau), 1)

    return poly[0] * 2.0


# gbm = log(cumsum(randn(100000)) + 1000)
# mr = log(randn(100000) + 1000)
# tr = log(cumsum(randn(100000) + 1) + 1000)
# fig = plt.figure()
# ax1 = fig.add_subplot(311)
# ax2 = fig.add_subplot(312)
# ax3 = fig.add_subplot(313)

# ax1.plot(gbm)
# ax1.set_title("gbm")
# ax2.plot(mr)
# ax2.set_title("mean reverting")
# ax3.plot(tr)
# ax3.set_title("trending")

# plt.tight_layout()

# print("Hurst(GBM): {}".format(hurst(gbm)))
# print("Hurst(MR): {}".format(hurst(mr)))
# print("Hurst(Tr): {}".format(hurst(tr)))

fig = plt.figure()
plt.plot(amzn["Adj Close"])
plt.title(label="Amazon Adj Close")
print("Hurst(amzn) : {}".format(hurst(amzn["Adj Close"])))
plt.show()
