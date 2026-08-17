# ---------------------------------------------------------------------------
# Stage 1 - build the React bundle.
#
# frontend/build is gitignored, so it is never present in a clone. Building it
# here keeps the image self-contained instead of depending on whoever runs
# `docker build` having run `npm run build` first. Without this, Django's SPA
# routes (/login, /register, /dealers, /dealer/<id>, /postreview/<id>) all fail
# with TemplateDoesNotExist because index.html is missing.
# ---------------------------------------------------------------------------
FROM node:18-bullseye-slim AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build


# ---------------------------------------------------------------------------
# Stage 2 - Django application.
# ---------------------------------------------------------------------------
FROM python:3.12.0-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV APP=/app

WORKDIR $APP

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . $APP

# Bring in the bundle produced by stage 1.
COPY --from=frontend /frontend/build $APP/frontend/build

EXPOSE 8000

# Collect frontend/static and frontend/build into STATIC_ROOT so gunicorn can
# serve them. Must run after the bundle is copied in.
RUN python3 manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "djangoproj.wsgi"]
