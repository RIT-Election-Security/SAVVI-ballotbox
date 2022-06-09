FROM python:3.9-bullseye

# Install prerequisite requirements
RUN apt-get update
RUN apt-get -y install python3-pip

# Install requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy in app code
RUN mkdir /app
WORKDIR /app
COPY run.py .
COPY app ./app

COPY docker/ca.crt /app/ca.crt

# Add CA cert to certifi bundle for requests
RUN cat /app/ca.crt >> `python -c 'import certifi; print(certifi.where())'`

# Run on port 0.0.0.0:80
CMD hypercorn --bind 0.0.0.0:80 app:app
