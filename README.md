# web-benchmarking

This project contains files to evaluate and benchmark normal and modified cache version.

## Before you start:

1. Install google chrome
2. Install requirements.txt

## Clone a website

To clone a website use self_hosting package.

```shell
PYTHONPATH=$(pwd) python self_hosting/entrypoint.py https://target-domain.com/ -sp /path/to/storage/ -cfp /path/to/Caddyfile
```

### arguments

- target-domain: Website you want clone. e.g.: `https://fa.wikipedia.org/`
- -sp: Your storage path. Website resources placed on it.
  - Note: Use absolute path. Because It will use on caddyfile
- -cfp: Caddyfile that configure caddy to server website will place on this path

## Run Webserver

Clone modified version of caddy. You can compile golang code to run webserver.

```shell
go mod download
go build -o newcaddy ./cmd/caddy
./newcaddy run --config /path/to/Caddyfile
```

`/path/to/Caddyfile` should copy from previous step

## Load Testing

To get a benchmark from 2 version (classic and our version), You can use load_testing package.
This step require one more step before running. To invalidate browser cache, we should change system time to future.
This process should run as sudo. To set Your password,
in load_testing/time_faker.py change `YOUR_PASSWORD` with your own.
Then,

```shell
python load_testing/entrypoint.py -r 3 http://localhost/target/
```

### arguments

- target: Is your target cloned in previous step without domain.
  - For example if your target is fa.wikipedia.org, `target` will be `fa.wikipedia`.
- -r: Is number of repeats. In each network condition code loads site `-r` times to get a median from response times.
