from matplotlib import pyplot as plt


def save_kv_file(data: dict, path):
    header = ','.join(map(str, data.keys()))
    row = ','.join(map(str, data.values()))
    with open(path, 'w+') as f:
        f.write('\n'.join((header, row)))


def plot_max_age_cdf(max_age_count: dict):
    pair_max_age_and_count = [(max_age, count) for max_age, count in max_age_count.items()]
    pair_max_age_and_count.sort(key=lambda item: item[0])
    sum_count = sum(pair[1] for pair in pair_max_age_and_count)

    pair_max_age_and_probability = [(max_age, count / sum_count) for max_age, count in pair_max_age_and_count]
    cumulative_probability = 0
    for i in range(len(pair_max_age_and_probability)):
        cumulative_probability += pair_max_age_and_probability[i][1]
        pair_max_age_and_probability[i] = (pair_max_age_and_probability[i][0], cumulative_probability)

    fig, (one_month_scale, one_year_scale, all_history) = plt.subplots(3, 1, figsize=(6, 10))
    month_pairs = list(filter(lambda pair: pair[0] <= 30, pair_max_age_and_probability))
    month_ticks = range(0, 31, 2)
    year_pairs = list(filter(lambda pair: pair[0] <= 365, pair_max_age_and_probability))
    year_ticks = range(0, 366, 30)
    all_history_pairs = pair_max_age_and_probability
    all_history_ticks = (0, 365, 1440, 2880, 5760, pair_max_age_and_probability[-1][0])

    for title, pairs, ticks, subplot in [
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
    plt.subplots_adjust(wspace=0.4,
                        hspace=0.4)
    plt.savefig(fname='max-age-cdf.jpg')
    plt.show()
