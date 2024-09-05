import argparse

import self_hosting.download

from load_testing.controller import LoadTesterController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("website", help=f"Which site you want monitor it.")
    parser.add_argument("-sp", "--caddy-serve-path", help="Where caddy will serve files.")
    parser.add_argument("-cfp", "--caddyfile-path", help="Where store caddyfile.", default="./Caddyfile")

    parser.add_argument("-r", "--repeats",
                        help="request count to same page to calculate resposne time by averaging them.",
                        default=1)

    args = parser.parse_args()

    print("Self hosting...")
    website_name = self_hosting.download.self_host(args.website, args.caddy_serve_path, args.caddyfile_path)

    input("Press enter after placing caddyfile (If you didn't pass -cfp) restarting caddy to start evaluation!")

    print("Evaluating...")
    LoadTesterController([f"http://localhost{website_name}"], "", args.repeats).calculate_and_plot()


if __name__ == '__main__':
    main()
