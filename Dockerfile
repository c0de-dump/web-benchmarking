FROM python:latest

ENV PYTHONPATH="/app"
WORKDIR /app

# Install Chrome
RUN apt-get update 
RUN apt-get install -y unzip curl libnss3 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libdrm2 libxkbcommon0 libasound2
RUN curl 'https://storage.googleapis.com/chrome-for-testing-public/130.0.6684.0/linux64/chrome-headless-shell-linux64.zip' \
    --output 'chrome-headless-shell.zip'  && unzip chrome-headless-shell.zip -d .
RUN curl 'https://storage.googleapis.com/chrome-for-testing-public/130.0.6684.0/linux64/chromedriver-linux64.zip' \
    --output 'chromedriver.zip'  && unzip chromedriver.zip -d .

RUN mv -f ./chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
RUN chown root:root /usr/local/bin/chromedriver
RUN chmod 0755 /usr/local/bin/chromedriver

# Move the source code into the container
COPY self_hosting ./self_hosting
COPY load_testing ./load_testing
COPY shared ./shared

# Install python dependencies
COPY pyproject.toml uv.lock ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin/:$PATH"
RUN uv sync

ENTRYPOINT ["uv", "run", "load_testing/entrypoint.py", "--chrome", "/app/chrome-headless-shell-linux64/chrome-headless-shell"]
