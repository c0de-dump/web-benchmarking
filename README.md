# web-benchmarking

This project contains files to evaluate and benchmark normal and modified cache version.

## How to
To download a website and evaluate modified version,
1. run `python startup/startup.py -sp /home/divar/websites -cfp /home/divar/Personal/Projects/caddy-cache/caddy/Caddyfile http://google.com/`
2. after downloading website, terminal wants you to restart caddy server and press enter.
3. file `evaluate.png` creates under current directory and you can see statistics.