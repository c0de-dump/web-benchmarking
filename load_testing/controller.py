import json
from typing import Type

import matplotlib.pyplot as plt
import numpy as np

from load_testing.load_tester import ClassicLoadTester, CacheV2LoadTester, LoadTester, NetworkCondition
from shared.logging import logger


class LoadTesterController:
    def __init__(self, website_list, chrome, repeats=3):
        self.repeats = repeats
        self.website_list = website_list
        self.chrome = chrome

    @classmethod
    def network_conditions(cls):
        return [
            NetworkCondition(latency=200, download=60 * 1024 * 1024, upload=60 * 1024 * 1024),
            NetworkCondition(latency=100, download=60 * 1024 * 1024, upload=60 * 1024 * 1024),
            NetworkCondition(latency=40, download=60 * 1024 * 1024, upload=60 * 1024 * 1024),

            NetworkCondition(latency=200, download=20 * 1024 * 1024, upload=20 * 1024 * 1024),
            NetworkCondition(latency=100, download=20 * 1024 * 1024, upload=20 * 1024 * 1024),
            NetworkCondition(latency=40, download=20 * 1024 * 1024, upload=20 * 1024 * 1024),

            NetworkCondition(latency=200, download=1 * 1024 * 1024, upload=1 * 1024 * 1024),
            NetworkCondition(latency=100, download=1 * 1024 * 1024, upload=1 * 1024 * 1024),
            NetworkCondition(latency=40, download=1 * 1024 * 1024, upload=1 * 1024 * 1024),
        ]

    @classmethod
    def load_testers(cls):
        return [
            ClassicLoadTester,
            CacheV2LoadTester,
        ]

    def log_stats(self, stats):
        print(stats)

        file_name = "_".join(self.website_list).replace("/", "_")
        stats_json = json.dumps(stats)
        with open(file_name, "w+") as f:
            f.write(stats_json)

    def calculate_and_plot(self):
        stats = self.calculate()

        self.log_stats(stats)

        # Initialize the plot
        num_websites = len(stats)
        num_conditions = max(len(stats) for stats in stats.values())
        fig, axs = plt.subplots(num_websites, num_conditions * 2,
                                figsize=(16 * len(self.network_conditions()), 8 * num_websites))

        # Ensure axs is 2D
        axs = np.atleast_2d(axs)

        for i, (website, network_conditions) in enumerate(stats.items()):
            for j, (network_condition, methods) in enumerate(network_conditions.items()):
                ax = axs[i, 2 * j]
                ax.set_title(f"{website}\n{network_condition}")

                for method, values in methods.items():
                    sorted_keys = sorted(values.keys(), key=int)
                    sorted_values = [values[key] for key in sorted_keys]

                    ax.plot(sorted_keys, sorted_values, label=method)

                ax.set_xlabel('Number of seconds passed')
                ax.set_ylabel('Load page time (ms)')
                ax.legend()
                ax.grid(True)

                # Plot enhancement
                ax_enhancement = axs[i, 2 * j + 1]
                ax_enhancement.set_title(f"Enhancement of CacheV2LoadTester vs ClassicLoadTester\n{network_condition}")

                classic_values = methods['ClassicLoadTester']
                cache_values = methods['CacheV2LoadTester']

                enhancement_keys = sorted(classic_values.keys(), key=int)
                enhancement_values = [
                    (classic_values[key] - cache_values[key]) / classic_values[key]
                    for key in enhancement_keys
                ]

                ax_enhancement.plot(enhancement_keys, enhancement_values, label='Enhancement')

                ax_enhancement.set_xlabel('Number of days passed')
                ax_enhancement.set_ylabel('Enhancement')
                ax_enhancement.legend()
                ax_enhancement.grid(True)

        plt.tight_layout()
        plt.savefig('./evaluate.png')

    def calculate(self):
        output = {}

        for website in self.website_list:
            for cond in self.network_conditions():
                for load_tester in self.load_testers():
                    logger.warning(
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
        median_dict = {}

        for i in range(self.repeats):
            logger.info(f"Repeat: {i}")
            load_tester = load_tester_class(condition)
            stats = load_tester.calculate_load_time(self.chrome, website)

            for stat_key, stat in stats.items():
                prev_stat = median_dict.get(stat_key, [])
                median_dict[stat_key] = prev_stat + [stat]
        result = {}
        for key, stats in median_dict.items():
            sorted_stats = sorted(stats)
            if (l := len(sorted_stats))%2==0:
                median = (sorted_stats[l//2-1] + sorted_stats[l//2]) // 2
            else:
                median = sorted_stats[l//2]
            result[key] = median

        return result
