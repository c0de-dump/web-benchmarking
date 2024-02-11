from matplotlib import pyplot as plt


def save_kv_file(data: dict, path):
    header = ','.join(map(str, data.keys()))
    row = ','.join(map(str, data.values()))
    with open(path, 'w+') as f:
        f.write('\n'.join((header, row)))


def calc_cdf(time_to_count: dict):
    pair_max_age_and_count = [(max_age, count) for max_age, count in time_to_count.items()]
    pair_max_age_and_count.sort(key=lambda item: item[0])
    sum_count = sum(pair[1] for pair in pair_max_age_and_count)

    pair_max_age_and_probability = [(max_age, count / sum_count) for max_age, count in pair_max_age_and_count]
    cumulative_probability = 0
    for i in range(len(pair_max_age_and_probability)):
        cumulative_probability += pair_max_age_and_probability[i][1]
        pair_max_age_and_probability[i] = (pair_max_age_and_probability[i][0], cumulative_probability)

    return pair_max_age_and_probability


def plot_max_age_cdf(max_age_count_hours: dict):
    hours_of_28_years = 28 * 365 * 24
    max_age_count_hours = {hour: count for hour, count in max_age_count_hours.items() if hour <= hours_of_28_years}
    lower_than_24_hours = {hour: count for hour, count in max_age_count_hours.items() if hour <= 24}

    max_age_count_days = {}
    for hour, count in max_age_count_hours.items():
        days = hour // 24
        max_age_count_days[days] = max_age_count_days.get(days, 0) + count

    pair_max_age_and_probability_days = calc_cdf(max_age_count_days)
    pair_max_age_and_probability_hours = calc_cdf(lower_than_24_hours)

    fig, (one_day_scale, one_month_scale, one_year_scale, all_history) = plt.subplots(4, 1, figsize=(6, 12))

    zero_day_probability = pair_max_age_and_probability_days[0][1]
    day_pairs = list(map(lambda pair: (pair[0], pair[1] * zero_day_probability), pair_max_age_and_probability_hours))
    day_ticks = range(0, 25, 2)

    month_pairs = list(filter(lambda pair: pair[0] <= 30, pair_max_age_and_probability_days))
    month_ticks = range(0, 31, 2)
    year_pairs = list(filter(lambda pair: pair[0] <= 365, pair_max_age_and_probability_days))
    year_ticks = range(0, 366, 30)
    all_history_pairs = pair_max_age_and_probability_days
    all_history_ticks = (0, 365, 1440, 2880, 5760, pair_max_age_and_probability_days[-1][0])

    for title, pairs, ticks, subplot in [
        ("first 24 hours view", day_pairs, day_ticks, one_day_scale),
        ("first month view", month_pairs, month_ticks, one_month_scale),
        ("first year view", year_pairs, year_ticks, one_year_scale),
        ("all history view", all_history_pairs, all_history_ticks, all_history)
    ]:
        xs = list(map(lambda pair: pair[0], pairs))
        ys = list(map(lambda pair: pair[1], pairs))
        subplot.set_xticks(ticks=ticks)
        subplot.set_title(title)
        subplot.plot(xs, ys)
    plt.xlabel(xlabel="in days")
    one_day_scale.set_xlabel("in hours")
    plt.subplots_adjust(wspace=0.4,
                        hspace=0.4)
    plt.savefig(fname='max-age-cdf.jpg')
    plt.show()
