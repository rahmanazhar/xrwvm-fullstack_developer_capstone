# Best Cars Dealerships — Full Stack Developer Capstone

**Project name:** Best Cars Dealerships (Car Dealership Review Portal)

A full stack car dealership review application. Visitors browse 50 dealerships,
filter them by state, and read customer reviews with an automatically computed
sentiment rating. Registered users sign in and post their own reviews, which are
scored by a sentiment analysis microservice as they are read back.

This is the capstone project for the IBM *Full Stack Application Development*
Professional Certificate.

## Architecture

Three independently deployable services:

```
Browser ──▶ Django :8000 ──┬──▶ Express API :3030 ──▶ MongoDB :27017
           (+ React SPA)   └──▶ Flask sentiment analyzer :5050
```

| Service | Path | Responsibility |
|---|---|---|
| Django + React | `server/` | User auth, car makes/models, page rendering, API proxy |
| Express + Mongoose | `server/database/` | Dealership and review persistence in MongoDB |
| Flask + nltk VADER | `server/djangoapp/microservices/` | Sentiment scoring of review text |

Django never talks to MongoDB directly. `server/djangoapp/restapis.py` reads both
downstream URLs from `server/djangoapp/.env`, which is what allows the identical
codebase to run locally and in a Kubernetes deployment.

### Django endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/djangoapp/register` | POST | Create a user and sign them in |
| `/djangoapp/login` | POST | Authenticate a user |
| `/djangoapp/logout` | GET | Destroy the session |
| `/djangoapp/get_dealers` | GET | All dealerships |
| `/djangoapp/get_dealers/<state>` | GET | Dealerships in one state (`All` for every one) |
| `/djangoapp/dealer/<id>` | GET | One dealership's details |
| `/djangoapp/reviews/dealer/<id>` | GET | A dealer's reviews, each with a sentiment |
| `/djangoapp/add_review` | POST | Post a review (authenticated users only) |
| `/djangoapp/get_cars` | GET | Car makes and models |

## Data model

- `CarMake` — name, description, country
- `CarModel` — foreign key to `CarMake`, name, type (Sedan/SUV/Wagon/Coupe/Hatchback),
  year (2015–2023)

Dealerships and reviews live in MongoDB, not in Django's database.

## Running it locally

**1. MongoDB + Express API**

The compose file references a pre-built image, so build it first:

```bash
cd server/database
docker build -t nodeapp .
docker compose up -d
curl http://localhost:3030/fetchDealers   # expect 50 dealerships
```

**2. Sentiment analyzer**

`nltk` resolves the VADER lexicon at import time, so place the bundled copy where
`nltk` looks for it before starting Flask — otherwise the service dies at startup:

```bash
mkdir -p ~/nltk_data/sentiment
cp server/djangoapp/microservices/sentiment/vader_lexicon.zip ~/nltk_data/sentiment/
cd server/djangoapp/microservices
pip install -r requirements.txt
flask run -p 5050
curl http://localhost:5050/analyze/Fantastic%20services   # {"sentiment": "positive"}
```

On Windows the lexicon path is `%APPDATA%\nltk_data\sentiment\`.

**3. Django + React**

```bash
cd server
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # Linux/macOS: .venv/bin/pip
cd frontend && npm install && npm run build && cd ..
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The React bundle is served out of `frontend/build`, so **re-run `npm run build`
after any change under `frontend/src`** or the change will not appear.

Open http://localhost:8000/.

## Deployment

See [LAB_DEPLOY.md](LAB_DEPLOY.md) for deploying the sentiment analyzer to IBM
Code Engine and the Django application to Kubernetes.

## Continuous integration

`.github/workflows/main.yml` lints every Python file with `flake8` and the Express
service's JavaScript with `jshint` on each push.

## Documentation

- [Build design](docs/superpowers/specs/2026-08-17-capstone-build-design.md)
- [Implementation plan](docs/superpowers/plans/2026-08-17-capstone-build.md)
