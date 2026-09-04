Create a Virtual EnvironmentA virtual environment keeps your project dependencies organized and isolated from other projects. Navigate to your preferred project directory and run:bash
         `python3 -m venv myenv`
Use code with caution.3. Activate the EnvironmentYou must activate the virtual environment 
Use code with caution.macOS / Linux:
         `source myenv/bin/activate`

after installation, if the installed package is not in the requirement.txt, then run
          `pip freeze > requirements.txt`

To generate EDGE_API_TOKEN
`python -c "import secrets; print(secrets.token_urlsafe(48))"`

Start the development server using the command:
`python3 manage.py runserver`

Run migrations
`python3 manage.py makemigrations`
`python3 manage.py migrate`

to sync users use
`python manage.py sync_edge_users`

python -m celery -A test_face_recog worker -l info
python -m celery -A test_face_recog beat -l info

## Face recognition

Uses OpenCV's built-in models — **YuNet** for detection and **SFace** for a
128-d embedding (`face_recognition/embeddings.py`). No insightface / onnxruntime
/ dlib, so it runs in-process in ~250 MB RAM (fits a free dyno).

The two ONNX files (~40 MB total) download from the OpenCV model zoo on first
use; the Docker build pre-fetches them into the image.

Matching is cosine similarity; `FACE_MATCH_THRESHOLD` (default `0.363`, OpenCV's
recommended SFace value) decides same/different identity.

> Changing the model changes the embedding format. Any embeddings stored by an
> earlier version must be re-enrolled.

## Deploying on Render (Docker)

Render builds the `Dockerfile` directly. Create a **Web Service** from this repo
with runtime = Docker. The container runs `migrate` then Gunicorn on `$PORT`.

Add a Render **PostgreSQL** instance and set these environment variables on the
web service:

| Var | Value |
|-----|-------|
| `DATABASE_URL` | Internal Database URL from the Render Postgres instance |
| `SECRET_KEY` | any long random string (currently hardcoded in settings) |
| `ALLOWED_HOSTS` | your `*.onrender.com` host (optional; `RENDER_EXTERNAL_HOSTNAME` is picked up automatically) |

`PORT` is provided by Render automatically. Redis / Celery vars are only needed
if you also run `worker` + `beat` services for edge-node sync.

Optional tuning: `FACE_MATCH_THRESHOLD`, `FACE_DET_SCORE`, `FACE_MAX_IMAGE_SIDE`.

Run a one-off edge sync from the Render shell if needed:

```bash
python manage.py sync_edge_users
```

### Why "Invalid or inactive e-ID." happened

`POST /api/v1/verify/` (`EdgeVerifyView`) only reads the `EdgeUser` replica
table, which is populated exclusively by `edge.sync.sync_users()` (Celery beat or
`manage.py sync_edge_users`). Right after registering + enrolling a face +
generating a QR code, no `EdgeUser` row exists yet, so the lookup raised
`DoesNotExist` -> "Invalid or inactive e-ID.".

The view now falls back to the central `EIDCard` / `FaceEmbedding` tables when no
`EdgeUser` matches, so verification works on a single-node deployment and before
the first sync. Running Celery `worker` + `beat` (or `manage.py sync_edge_users`)
keeps the edge replica populated for true offline edge nodes.