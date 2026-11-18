FROM python:3.11-slim

RUN pip install --no-cache-dir "python-chess==1.999"

WORKDIR /workspace

COPY solve.py /workspace/solution/solve.py
COPY test_example.py /workspace/solution/test_example.py
