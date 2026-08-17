FROM python:3.12.0-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV APP=/app

WORKDIR $APP

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . $APP

EXPOSE 8000

# The React bundle in frontend/build and the pages in frontend/static are
# collected into STATIC_ROOT so gunicorn can serve them without runserver's
# development static handler.
RUN python3 manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "djangoproj.wsgi"]
