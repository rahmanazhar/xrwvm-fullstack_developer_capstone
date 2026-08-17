# Capstone Build Design — xrwvm-fullstack_developer_capstone

**Date:** 2026-08-17
**Fork:** https://github.com/rahmanazhar/xrwvm-fullstack_developer_capstone
**Goal:** Satisfy all 28 rubric tasks (both the auto-graded artifact list and the
peer-graded screenshot list) with genuine, reproducible outputs.

## 1. Ground truth established before design

All of the following was read from the cloned repo or seed data, not recalled.

| Fact | Consequence |
|---|---|
| `models.py`, `admin.py`, `populate.py`, `restapis.py`, `urls.py` are comment-only stubs | Full implementation required |
| `views.py` contains only `login_user` | `logout`, `registration`, 4 dealer views, `get_cars`, `add_review` required |
| `static/Contact.html` does not exist | Create from scratch (Task 4) |
| `components/Register/Register.jsx` does not exist (only its `.css`) | Create from scratch (Task 7) |
| `Dealers.jsx`, `Dealer.jsx`, `PostReview.jsx`, `Login.jsx`, `Header.jsx` are **complete** | Do not rewrite; treat as the API contract |
| `App.js` routes `/login` only | Add `register`, `dealers`, `dealer/:id`, `postreview/:id` |
| `settings.py` has empty `TEMPLATES.DIRS`, `STATICFILES_DIRS`, `ALLOWED_HOSTS` | Must be wired to `frontend/static` + `frontend/build` |
| `app.js` stubs `/fetchDealers`, `/fetchDealers/:state`, `/fetchDealer/:id` | Implement 3 routes |
| `app.js` connects to host `mongo_db` | Express is only runnable inside docker-compose |
| `docker-compose.yml` `api` service uses `image: nodeapp` with **no `build:`** | Must `docker build -t nodeapp .` before `docker compose up` |
| `database/Dockerfile` does `ADD data/*.json .` | `fs.readFileSync("reviews.json")` resolves — confirmed, not assumed |
| `microservices/app.py` ends in `app.run(debug=True)` → port 5000 | Run via `flask run -p 5050` to match `.env` default; do not edit course file |
| Seed data: 50 dealers, 50 reviews | — |
| Kansas has exactly 1 dealer: **id 8, Bytecard Car Dealership** | Task 11 output is a 1-element array by design |
| Dealer **17** has 4 reviews, dealer **15** has 3, rest ≤2 | Tasks 8 and 20 use dealer 15 |
| No `.github/workflows/` | Create `main.yml` (Task 23) |

## 2. Runtime topology

```
Browser ──▶ Django :8000 ──┬──▶ Express :3030 ──▶ MongoDB :27017   (docker compose)
           (venv, native)  └──▶ Flask   :5050                      (venv, native)
```

`.env`: `backend_url=http://localhost:3030`, `sentiment_analyzer_url=http://localhost:5050/`

Port 8000 was occupied by an unrelated `fxbot` dashboard; stopped with the user's
explicit confirmation after its true identity was reported.

## 3. API contract (derived from the finished frontend)

The existing JSX fixes these shapes. Deviating produces blank pages, not errors —
which is why this table is the spec's load-bearing section.

| Endpoint | Method | Response shape | Consumer |
|---|---|---|---|
| `/djangoapp/login` | POST | `{userName, status:"Authenticated"}` | `Login.jsx` |
| `/djangoapp/logout` | GET | `{userName:""}` (truthy) | `Header.jsx` |
| `/djangoapp/register` | POST | `{userName, status:"Authenticated"}` | `Register.jsx` |
| `/djangoapp/get_dealers` | GET | `{status:200, dealers:[...]}` | `Dealers.jsx` |
| `/djangoapp/get_dealers/<state>` | GET | `{status:200, dealers:[...]}`; `All` ⇒ every dealer | `Dealers.jsx` |
| `/djangoapp/dealer/<id>` | GET | `{status:200, dealer:[{...}]}` — **array under singular key** | `Dealer.jsx`, `PostReview.jsx` |
| `/djangoapp/reviews/dealer/<id>` | GET | `{status:200, reviews:[{review,name,car_make,car_model,car_year,sentiment}]}` | `Dealer.jsx` |
| `/djangoapp/get_cars` | GET | `{CarModels:[{CarModel, CarMake}]}` | `PostReview.jsx` |
| `/djangoapp/add_review` | POST | `{status:200}` | `PostReview.jsx` |

`sentiment` is not stored in Mongo — Django enriches each review by calling the
Flask service per review at read time.

## 4. Phases, each with its verification oracle

A phase is done when its oracle passes, not when its code is written.

| # | Tasks | Work | Oracle |
|---|---|---|---|
| 0 | 1, 2 | Fork, clone, README, venv, `npm run build`, migrate, `root` superuser | `runserver` serves `/` 200; output captured to `django_server` |
| 1 | 3, 4 | `About.html` rewrite, new `Contact.html` | Both render with CSS applied in a real browser |
| 2 | 5, 6, 7 | `logout_request`, `registration`, `urls.py`, `Register.jsx`, `App.js` routes | curl login returns `Authenticated`; logout returns 200 |
| 3 | 8–11 | 3 `app.js` routes; `docker build` + `compose up` | 4 curls return non-empty JSON; Kansas returns dealer 8 |
| 4 | 12–15 | `CarMake`/`CarModel`, `admin.py`, `populate.py`, migrations | `/djangoapp/get_cars` lists makes+models; admin pages screenshot |
| 5 | 16 | vader lexicon, Flask on 5050, `analyze_review_sentiments` | `analyze/Fantastic services` ⇒ `{"sentiment":"positive"}` |
| 6 | 17–22 | `get_request`/`post_review`, 4 dealer views, wire routes | 6 browser screenshots; posted review appears on dealer page |
| 7 | 23 | `.github/workflows/main.yml` (flake8 + jshint) | `gh run` concludes **success**; log captured to `CICD` |
| 8 | 24–28 | `LAB_DEPLOY.md` runbook for Code Engine + Kubernetes | User executes in Skills Network lab |

Riskiest-first exception to strict ordering: the vader lexicon (Phase 5) and the
Docker build (Phase 3) are smoke-tested early, because both fail in ways that are
cheap to fix now and expensive to discover during screenshot capture.

## 5. Artifacts, all at repo root

**Text** (real `curl.exe` / terminal output, never hand-written): `django_server`,
`loginuser`, `logoutuser`, `getdealerreviews`, `getalldealers`, `getdealerbyid`,
`getdealersbyState`, `getallcarmakes`, `analyzereview`, `CICD`, `deploymentURL`

**Screenshots** (Playwright against the running app): `admin_login.png`,
`admin_logout.png`, `get_dealers.png`, `get_dealers_loggedin.png`,
`dealersbystate.png`, `dealer_id_reviews.png`, `dealership_review_submission.png`,
`added_review.png`, plus deployed: `deployed_landingpage.png`,
`deployed_loggedin.png`, `deployed_dealer_detail.png`, `deployed_add_review.png`

Tasks 18, 19, 20, 22, 25–28 require a visible address bar, so those captures are
full-window, not viewport-only.

## 6. Content decisions

- **About/Contact personas are fictional.** Invented names, roles, bios; emails on
  the app's own fictional domain. No real person's photo, name, or address goes
  into a public repo.
- Portraits from `randomuser.me` stock URLs — realistic, no repo bloat.
- `Contact.html` marks **Contact Us** active in the nav, per the rubric's wording.
- Superuser is `root` (rubric says "root user"). Its password is never committed.

## 7. Deliberately out of scope

- No rewrite of the working JSX components, and no unrelated refactoring.
- `requirements.txt` stays unpinned; resolved versions are recorded in the
  `django_server` artifact so the build is reproducible after the fact.
- Django's `USE_L10N` is a no-op on Django 5.x. Left as shipped — harmless, and
  editing course-provided settings invites lint churn for zero rubric gain.

## 8. Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| nltk cannot find `vader_lexicon` | `SentimentIntensityAnalyzer()` raises at import, so Flask dies at startup, not at request time | Place the shipped zip under `~/nltk_data/sentiment/`; verify before Phase 5 |
| Unpinned Django resolves to 5.x | Settings were generated for 3.2 | Run the server early (Phase 0) — a mismatch fails loudly at boot |
| `compose up` without a built image | `image: nodeapp` has no `build:`, so compose fails on a missing image | Explicit `docker build -t nodeapp .` first |
| Sentiment call per review | A slow Flask service makes the dealer page appear to hang | Acceptable at 50 reviews; noted, not optimised |
| Phase 8 is not locally verifiable | Deployed screenshots cannot be produced from this machine | Delivered as a runbook; user executes and captures |
