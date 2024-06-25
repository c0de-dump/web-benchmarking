from typing import Type

import matplotlib.pyplot as plt

from load_testing.load_tester import ClassicLoadTester, CacheV2LoadTester, LoadTester, NetworkCondition


class LoadTesterController:
    def __init__(self, website_list, repeats=1):
        self.repeats = repeats
        self.website_list = website_list

    @classmethod
    def network_conditions(cls):
        return [
            NetworkCondition(latency=5, download=500 * 1024, upload=500 * 1024),
            NetworkCondition(latency=10, download=300 * 1024, upload=300 * 1024)
        ]

    @classmethod
    def load_testers(cls):
        return [
            ClassicLoadTester,
            CacheV2LoadTester,
        ]

    def calculate_and_plot(self):
        stats = self.calculate()

        # Initialize the plot
        num_websites = len(stats)
        fig, axs = plt.subplots(num_websites, max(len(stats) for stats in stats.values()),
                                figsize=(15, 8 * num_websites))

        if num_websites == 1:
            axs = [axs]

        for i, (website, network_conditions) in enumerate(stats.items()):
            if len(network_conditions) == 1:
                axs[i] = [axs[i]]

            for j, (network_condition, methods) in enumerate(network_conditions.items()):
                ax = axs[i][j]
                ax.set_title(f"{website}\n{network_condition}")

                for method, values in methods.items():
                    sorted_keys = sorted(values.keys(), key=int)
                    sorted_values = [values[key] for key in sorted_keys]

                    ax.plot(sorted_keys, sorted_values, label=method)

                ax.set_xlabel('Number of days passed')
                ax.set_ylabel('Page load time (ms)')
                ax.legend()
                ax.grid(True)

        plt.tight_layout()
        plt.show()

    def calculate(self):
        output = {}

        for website in self.website_list:
            for cond in self.network_conditions():
                for load_tester in self.load_testers():
                    print(
                        f"Calculate load time test for {website} "
                        f"with network condition {cond} "
                        f"by {load_tester.name()}")

                    load_stats = self._calc(load_tester, cond, website)

                    website_stats = output.get(website, {})
                    condition_stats = website_stats.get(cond.name(), {})

                    condition_stats[load_tester.name()] = load_stats
                    website_stats[cond.name()] = condition_stats
                    output[website] = website_stats

        return output

    def _calc(self, load_tester_class: Type[LoadTester], condition: NetworkCondition, website):
        average_dict = {}

        for i in range(self.repeats):
            load_tester = load_tester_class(condition)
            stats = load_tester.calculate_load_time(website)
            for stat_key, stat in stats.items():
                prev_stat = average_dict.get(stat_key, 0)
                average_dict[stat_key] = (prev_stat * i + stat) / (i + 1)

        return average_dict
