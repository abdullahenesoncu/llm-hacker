FROM python:3.11-slim

RUN pip install --no-cache-dir "python-chess==1.999" "pytest>=7.0.0"

WORKDIR /workspace

COPY . /tests
