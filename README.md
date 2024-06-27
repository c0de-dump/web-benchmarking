# web-benchmarking

This project contains files to evaluate and benchmark normal and modified cache version.

## How to

To download a website and evaluate modified version:
1. export `CHANGE_TIME_PASSWORD` variable with sudo password value. `export CHANGE_TIME_PASSWORD=<password>` 
2. run `python startup/startup.py -sp /home/divar/websites -cfp /home/divar/Personal/Projects/caddy-cache/caddy/Caddyfile http://google.com/`
3. after downloading website, terminal wants you to restart caddy server and press enter.
4. file `evaluate.png` creates under current directory, and you can see statistics.

### Note

Sudo password required for changing time to simulate time passing.
After ending process, time will set to `sync with server`. But you can manually run `timedatectl set-ntp 1`
