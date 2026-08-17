# Submission Index

Repo: https://github.com/rahmanazhar/xrwvm-fullstack_developer_capstone

Every artifact below was produced by running the real services — curl output is
captured verbatim, screenshots are of a real browser against the running app.
Nothing here is hand-written to look like program output.

`BLOB` below = `https://github.com/rahmanazhar/xrwvm-fullstack_developer_capstone/blob/main`

## Option 1 — Auto-graded (58 points)

| # | Pts | Deliverable | Where |
|---|---|---|---|
| 1 | 1 | README URL | [BLOB/README.md](README.md) |
| 2 | 1 | Django server terminal output | [BLOB/django_server](django_server) |
| 3 | 3 | About.html URL | [BLOB/server/frontend/static/About.html](server/frontend/static/About.html) |
| 4 | 2 | Contact.html URL | [BLOB/server/frontend/static/Contact.html](server/frontend/static/Contact.html) |
| 5 | 2 | Login cURL + output | [BLOB/loginuser](loginuser) |
| 6 | 2 | Logout cURL + output | [BLOB/logoutuser](logoutuser) |
| 7 | 1 | Register.jsx URL | [BLOB/server/frontend/src/components/Register/Register.jsx](server/frontend/src/components/Register/Register.jsx) |
| 8 | 2 | Dealer reviews cURL | [BLOB/getdealerreviews](getdealerreviews) |
| 9 | 2 | All dealers cURL | [BLOB/getalldealers](getalldealers) |
| 10 | 2 | Dealer by id cURL | [BLOB/getdealerbyid](getdealerbyid) |
| 11 | 2 | Dealers in Kansas cURL | [BLOB/getdealersbyState](getdealersbyState) |
| 12 | 2 | Admin login screenshot | `admin_login.png` |
| 13 | 1 | Admin logout screenshot | `admin_logout.png` |
| 14+15 | 4 | Car makes/models cURL | [BLOB/getallcarmakes](getallcarmakes) |
| 16 | 2 | Sentiment "Fantastic services" | [BLOB/analyzereview](analyzereview) |
| 17 | 1 | Dealers before login | `get_dealers.png` |
| 18 | 2 | Dealers after login | `get_dealers_loggedin.png` |
| 19 | 2 | Dealers filtered by state | `dealersbystate.png` |
| 20 | 1 | Dealer detail + reviews | `dealer_id_reviews.png` |
| 21 | 1 | Review form before submit | `dealership_review_submission.png` |
| 22 | 2 | Review after submit | `added_review.png` |
| 23 | 3 | CI/CD run output | [BLOB/CICD](CICD) |
| 24 | 1 | Deployment URL | [BLOB/deploymentURL](deploymentURL) — **done**, deployed to IBM Kubernetes |
| 25 | 2 | Deployed landing page | `deployed_landingpage.png` |
| 26 | 2 | Deployed logged-in page | `deployed_loggedin.png` |
| 27 | 2 | Deployed dealer detail | `deployed_dealer_detail.png` |
| 28 | 2 | Deployed added review | `deployed_add_review.png` |

## Option 2 — Peer-graded (50 points)

Same repo. Extra screenshots captured for the peer rubric's different asks:

| # | Deliverable | File |
|---|---|---|
| 3 | About Us page | `about_us.png` |
| 4 | Contact Us page | `contact_us.png` |
| 5 | Login page | `login_page.png` |
| 6 | Logout alert | `logout_alert.png` |
| 7 | Sign-Up page | `signup_page.png` |
| 8 | Dealer reviews via Express endpoint | `dealer_reviews_endpoint.png` |
| 9 | All dealers via Express endpoint | `all_dealers_endpoint.png` |
| 10 | Dealer detail via Express endpoint | `dealer_detail_endpoint.png` |
| 11 | Kansas dealers via Express endpoint | `kansas_dealers_endpoint.png` |
| 14 | Car makes | `cars.png` |
| 15 | Car models from admin | `car_models_admin.png` |
| 16 | Sentiment analyzer in browser | `sentiment_analyzer.png` |
| 23 | CI/CD success on GitHub | `cicd_github.png` |

## Deployment — complete

All 28 tasks are done. The application is deployed to the lab Kubernetes cluster:

```
https://rahmanprojec-8000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/
```

Four services, verified live end to end:

| Component | Where |
|---|---|
| Django + React | Kubernetes `dealership` deployment |
| Express API | Kubernetes `dealership-api` |
| MongoDB | Kubernetes `mongo-db` |
| Sentiment analyzer | Code Engine `sentianalyzer` |

Confirmed from outside the cluster: all SPA routes return 200, `get_dealers`
returns 50 dealers through Express and Mongo, `get_cars` returns 18 models, and
the review posted through the deployed UI came back scored **positive** by the
Code Engine analyzer.

Two things to know about this deployment:

- **The URL is tied to the lab session.** It stops working when the lab expires,
  which is expected — the screenshots are the durable evidence.
- **Restarting the `dealership-api` pod wipes posted reviews**, because `app.js`
  re-seeds its collections on every start. Restarting the `dealership` pod wipes
  the SQLite users, so re-run `migrate` and re-create users after any rollout.

## Reference values used

| Thing | Value | Why |
|---|---|---|
| Demo user | `hazhar` / `CarsReview#2026` | Used in `loginuser`, `logoutuser` and every logged-in screenshot |
| Admin user | `root` | Password deliberately not committed |
| Canonical dealer | **15** — Tempsoft, San Antonio, Texas | One of only two dealers with 3+ reviews |
| Kansas dealer | **8** — Bytecard, Topeka | The only dealer in Kansas, so Task 11 returns a single row by design |
| Filter state shown | Texas (8 dealers) | Multiple rows make the filter unambiguous; Kansas alone would look broken |
| Review posted | "Fantastic dealership and excellent service" / Toyota Camry / 2022 / 2026-07-15 | Kept short on purpose — see below |

### Why the review text is short

`microservices/app.py` classifies by comparing VADER's `pos`/`neu`/`neg`
**proportions**. Those sum to 1, so in any long sentence the neutral share
dominates and the review comes out "neutral" no matter how positive it reads.
That is the provided microservice's behaviour, left unmodified because Task 16
depends on it. A short review scores `positive`, which is why Tasks 21/22 use one.
