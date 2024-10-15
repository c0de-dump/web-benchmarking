FROM python:latest AS build

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

ENV PYTHONPATH="/app"

FROM build AS self_hosting

COPY self_hosting/ ./self_hosting
COPY shared/ ./shared

ENTRYPOINT ["python", "self_hosting/entrypoint.py"]

FROM build AS load_testing

RUN apt-get update && apt-get install -y unzip curl libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
     libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libdrm2 libxkbcommon0 libasound2

RUN curl 'https://storage.googleapis.com/chrome-for-testing-public/130.0.6684.0/linux64/chrome-headless-shell-linux64.zip' \
    --output '/chrome-headless-shell.zip'  && unzip /chrome-headless-shell.zip -d .
RUN curl 'https://storage.googleapis.com/chrome-for-testing-public/130.0.6684.0/linux64/chromedriver-linux64.zip' \
    --output '/chromedriver.zip'  && unzip /chromedriver.zip -d .

RUN mv -f ./chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
RUN chown root:root /usr/local/bin/chromedriver
RUN chmod 0755 /usr/local/bin/chromedriver

COPY load_testing/ ./load_testing
COPY shared/ ./shared

RUN apt-get install git

WORKDIR /
RUN git clone https://github.com/wolfcw/libfaketime.git
WORKDIR /libfaketime/src
RUN make install

WORKDIR /app
ENV LD_PRELOAD='/usr/local/lib/faketime/libfaketimeMT.so.1'
ENV FAKETIME_NO_CACHE=1

# https://github.com/cypress-io/cypress/issues/4925#issuecomment-2186494559
RUN service dbus start

ENTRYPOINT ["python", "load_testing/entrypoint.py", "--chrome", "/app/chrome-headless-shell-linux64/chrome-headless-shell"]
