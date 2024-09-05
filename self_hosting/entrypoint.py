import argparse
from shared.logging import logger

import download

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("website", help=f"Website to clone")
    parser.add_argument("-sp", "--caddy-serve-path", help="Where caddy will serve files")
    parser.add_argument("-cfp", "--caddyfile-path", help="Where store Caddyfile")
    args = parser.parse_args()

    website_name = download.self_host(args.website, args.caddy_serve_path, args.caddyfile_path)
    logger.warning(f"website {website_name} written to {args.caddy_serve_path}"
                f" and Caddyfile writen to {args.caddyfile_path}")


if __name__ == '__main__':
    main()