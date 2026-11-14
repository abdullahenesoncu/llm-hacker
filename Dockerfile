FROM python:3.11

# Sistem paketlerini yükle (derleyici ve kütüphaneler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    liboctomap-dev \
    libfcl-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Python paketlerini yükle
RUN pip install --no-cache-dir \
    trimesh \
    numpy \
    scipy \
    scikit-learn \
    pybullet \
    python-fcl \
    pytest \
    matplotlib

WORKDIR /app

# STL dosyalarını kopyala
COPY bottom.stl /app/
COPY top.stl /app/

# Test scriptini kopyala
COPY test_assembly.py /app/

# Test dosyalarını kopyala
COPY tests/ /app/tests/

CMD ["pytest", "-v", "tests/"]
