# Base image - tried a few others, this one was the easiest and most resilient
FROM python:3.10.0-slim-buster

# Specify root directory in image
WORKDIR /app/dash

# Installing python requirements
COPY ./src/requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

# Copy dash files to image
COPY . /app/dash

# Run dashboard
CMD cd /app/dash/src && waitress-serve --host=0.0.0.0 --port=80 --call app:returnApp 