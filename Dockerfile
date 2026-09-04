FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# opencv-python-headless needs libglib at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-fetch the OpenCV face models so the first request doesn't download them.
ENV FACE_MODEL_DIR=/app/models
RUN python -c "from face_recognition.embeddings import _model_path, _DETECTOR_FILE, _RECOGNIZER_FILE; _model_path(_DETECTOR_FILE); _model_path(_RECOGNIZER_FILE)"

# Face embeddings run in-process (OpenCV YuNet + SFace, ~250 MB RAM).
# Edge-user sync is handled by the celery beat schedule, not at boot.
CMD sh -c "python manage.py migrate --noinput && gunicorn test_face_recog.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --threads ${WEB_THREADS:-4} --timeout ${WEB_TIMEOUT:-120}"
