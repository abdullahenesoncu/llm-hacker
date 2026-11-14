FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ \
    liboctomap-dev libfcl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir \
    trimesh \
    pytest \
    pytest-html \
    scipy \
    numpy \
    matplotlib \
    pybullet

CMD ["python", "test.py"]
