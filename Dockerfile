FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System libraries for build tools, OpenCV, and dlib/ONNX runtimes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Cache the insightface model weights inside the image layer's default location
ENV INSIGHTFACE_HOME=/app/.insightface

# Default: run migrations and start Gunicorn on the dynamic port.
# The celery worker/beat containers override this command in docker-compose.
# Edge-user sync is handled by the celery beat schedule, not at boot.
CMD sh -c "python manage.py migrate --noinput && gunicorn test_face_recog.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --timeout 120"