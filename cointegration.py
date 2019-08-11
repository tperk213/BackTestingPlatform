import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pandas_datareader.data as web
import statsmodels.tsa.stattools as ts

import statsmodels.formula.api as sm


def plot_price_series(df, ts1, ts2):
    months = mdates.MonthLocator()
    fig, ax = plt.subplots()
    ax.plot(df.index, df[ts1], label=ts1)
    ax.plot(df.index, df[ts2], label=ts2)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.set_xlim(datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1))
    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel("Month/Year")
    plt.ylabel("Price ($)")
    plt.title("{} and {} Daily PRices".format(ts1, ts2))
    plt.legend()
    plt.show()


def plot_scatter_series(df, ts1, ts2):
    plt.xlabel("{} Price ($)".format(ts1))
    plt.ylabel("{} Price ($)".format(ts2))
    plt.title("{} and {} Price Scatterplot".format(ts1, ts2))
    plt.scatter(df[ts1], df[ts2])
    plt.show()


def plot_residuals(df):
    months = mdates.MonthLocator()
    fig, ax = plt.subplots()
    ax.plot(df.index, df["res"], label="Residuals")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.set_xlim(datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1))
    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel("Month/Year")
    plt.ylabel("Price($)")
    plt.title("Residuals")
    plt.legend()

    plt.plot(df["res"])
    plt.show()


if __name__ == "__main__":
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2015, 1, 1)

    arex = web.DataReader("AREX", "yahoo", start, end)
    arex.to_csv()
    wll = web.DataReader("WLL", "yahoo", start, end)
    wll.to_csv()
    df = pd.DataFrame(index=arex.index)
    df["AREX"] = arex["Adj Close"]
    df["WLL"] = wll["Adj Close"]

    # plot the two time series
    plot_price_series(df, "AREX", "WLL")

    plot_scatter_series(df, "AREX", "WLL")

    # Calculate the optimal hedge ratio
    res = sm.ols(formula="WLL ~ AREX", data=df).fit()
    beta_hr = res.params["AREX"]
    df["res"] = df["WLL"] - beta_hr * df["AREX"]

    plot_residuals(df)

    cadf = ts.adfuller(df["res"])
    print(cadf)
