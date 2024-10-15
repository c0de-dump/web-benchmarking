# web-benchmarking

This project contains files to evaluate and benchmark normal and modified cache version.

## How to

We have 3 parts. Download a website, Serve it in webserver and measure site loading time.
```bash
# Build Docker images
sudo docker build . -t loadtest:v1 --target=load_testing # Run in web-benchmarking project
sudo docker build . -t selfhosting:v1 --target=self_hosting # Run in web-benchmarking project
sudo docker build . -t caddy:v1 # Run in modified caddy project
sudo docker volume create selfhosting # Use for sharing data between site downloader and caddy
sudo docker volume create loadtesting # Use for saving evaluation metrics.

# Clone a website
sudo docker run -v selfhosting:/tmp/storage selfhosting:v1 <WEBSITE_TO_DOWNLOAD: ex) https://www.varzesh3.com/> -sp /tmp/storage/ -cfp /tmp/storage/Caddyfile

# Run webserver
sudo docker run -v selfhosting:/tmp/storage --name caddy -d caddy:v1

# Run load tester
- sudo docker run --memory=4g --network=container:caddy -v loadtesting:/tmp/result loadtest:v1 http://localhost/<SITE_NAME_WITHOUT_DOMAIN: ex) varzesh3>/
```
Now you can see result as a png picture in the following path:
```
/var/lib/docker/volumes/loadtesting/_data/evaluate.png
```
