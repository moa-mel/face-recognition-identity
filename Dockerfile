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

# Run migrations, (optional) sync edge users, and start Gunicorn on Render's dynamic port
CMD sh -c "python manage.py migrate --noinput && python manage.py sync_edge_users && gunicorn test_face_recog.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120"