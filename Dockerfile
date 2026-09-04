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

# Download the insightface model at build time so the first request does not
# have to fetch ~300 MB before it can respond.
ENV INSIGHTFACE_HOME=/app/.insightface
RUN python -c "from insightface.app import FaceAnalysis; app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider']); app.prepare(ctx_id=-1, det_size=(640, 640))"

COPY . .

# The celery worker/beat containers override this command in docker-compose.
# Edge-user sync is handled by the celery beat schedule, not at boot.
CMD sh -c "python manage.py migrate --noinput && gunicorn test_face_recog.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --threads ${WEB_THREADS:-2} --timeout ${WEB_TIMEOUT:-300}"
