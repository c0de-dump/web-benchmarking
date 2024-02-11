import pandas as pd

from statistics import plot_max_age_cdf

if __name__ == '__main__':
    with open("./max_age_count.csv") as f:
        data = f.read()
        header, row = data.split("\n")
        days = header.split(",")
        count = row.split(",")
        days = list(map(int, days))
        count = list(map(int, count))
        pair = filter(lambda x: x[0] < 10020, zip(days, count))
        plot_max_age_cdf({day: count for day, count in pair})
