# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Install necessary system utilities and Python 3.11
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-distutils curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /api

COPY . /api

RUN pip install --no-cache-dir --upgrade --upgrade-strategy eager -r requirements.txt

EXPOSE 8080

CMD ["python3.11", "src/api.py"]
