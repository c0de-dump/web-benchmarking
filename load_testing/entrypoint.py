import argparse

from load_testing.controller import LoadTesterController
from shared.logging import logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help=f"Which url you want monitor it.")
    parser.add_argument(
        "-c", "--chrome",
        help="Chrome binary location",
        default="",
    )
    parser.add_argument(
        "-r", "--repeats",
        help="request count to same page to calculate resposne time by averaging them.",
        default=1,
    )
    args = parser.parse_args()

    LoadTesterController([args.target], args.chrome, args.repeats).calculate_and_plot()


if __name__ == '__main__':
    main()
