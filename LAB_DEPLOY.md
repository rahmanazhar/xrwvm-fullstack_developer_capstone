# Deployment Runbook (Skills Network Lab)

Everything in Tasks 1–23 was built and verified locally. This runbook covers the
five artifacts that can only be produced from inside the IBM Cloud lab:
`deploymentURL`, `deployed_landingpage`, `deployed_loggedin`,
`deployed_dealer_detail`, `deployed_add_review`.

## Confidence note — read this first

| Part | Status |
|---|---|
| Application code, Dockerfile, `deployment.yaml`, env-var wiring | **Verified locally** — the image builds and the app runs |
| `ibmcloud ce` / `kubectl` command syntax, registry namespace variables, lab proxy URL scheme | **Not verifiable from outside the lab** — cross-check each against your lab instructions before running |

The IBM lab rotates CLI syntax and environment-variable names between course
revisions. Where a command below differs from your lab sheet, **the lab sheet
wins**. The parts that matter and are verified are the two URLs the app needs
and the fact that both are read from the environment.

## What has to be true for the deployed app to work

Three services, exactly as locally:

```
Browser ──▶ Django (Kubernetes) ──┬──▶ Express + Mongo   (backend_url)
                                  └──▶ Flask sentiment   (sentiment_analyzer_url)
```

Two environment variables carry those addresses. Get them wrong and the
symptom is a **blank dealer table with no error**, because `restapis.get_request`
logs the failure and returns `None`.

- `backend_url` — no trailing slash, e.g. `http://mongo-express-service:3030`
- `sentiment_analyzer_url` — **must end in `/`**, because `restapis.py` does
  `sentiment_analyzer_url + "analyze/" + text`

## Part A — Sentiment analyzer to Code Engine

```bash
cd server/djangoapp/microservices

# The lab exposes your registry namespace as an env var; confirm its name.
echo $SN_ICR_NAMESPACE

docker build -t us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer .
docker push us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer

ibmcloud target -g Default
ibmcloud ce project create --name sentianalyzer   # skip if it already exists
ibmcloud ce project select --name sentianalyzer

ibmcloud ce application create \
  --name sentianalyzer \
  --image us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer \
  --registry-secret icr-secret \
  --port 5000

ibmcloud ce application get --name sentianalyzer --output url
```

**The container listens on 5000**, not 5050 — `microservices/Dockerfile` runs
`flask run --host=0.0.0.0` with Flask's default port. 5050 is only the local
convention. Set `--port 5000`.

Verify before moving on — this is the same check the rubric's Task 16 asks for:

```bash
curl "https://<your-code-engine-url>/analyze/Fantastic%20services"
# expect: {"sentiment": "positive"}
```

If it returns a 500, the VADER lexicon is missing inside the image. See the
lexicon note in [README.md](README.md#running-it-locally).

## Part B — Express + MongoDB

Deploy the `server/database` service so the cluster can reach it, then note its
in-cluster address for `backend_url`. If your lab instead runs this with
`docker compose` on the lab VM, use the address the lab gives you.

```bash
cd server/database
docker build -t us.icr.io/$SN_ICR_NAMESPACE/dealership-api .
docker push us.icr.io/$SN_ICR_NAMESPACE/dealership-api
```

Note: `app.js` connects to the literal host `mongo_db`, so whatever runs Mongo
must be reachable under that name — or change the connection string in
`app.js:14` to match your service name.

Also note: `app.js` wipes and re-seeds both collections **on every start**, so a
pod restart erases posted reviews. Capture `deployed_add_review` without
restarting the API pod in between.

## Part C — Django to Kubernetes

1. Put the Code Engine URL into `server/djangoapp/.env` (trailing slash), or
   better, set it via `deployment.yaml` env vars so the image stays generic.

2. Edit `server/deployment.yaml`:
   - replace `<NAMESPACE>` in the image with `$SN_ICR_NAMESPACE`
   - set `sentiment_analyzer_url` to the Part A URL
   - set `backend_url` to the Part B address

3. Build, push, deploy:

```bash
cd server
docker build -t us.icr.io/$SN_ICR_NAMESPACE/dealership .
docker push us.icr.io/$SN_ICR_NAMESPACE/dealership
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs deployment.apps/dealership
```

4. Allow the public hostname. Django rejects unknown hosts with
   **DisallowedHost (400)**, which looks like a broken deployment. Add to the
   container's `env:` in `deployment.yaml`:

```yaml
- name: DJANGO_ALLOWED_HOSTS
  value: "<your-public-host>,localhost,127.0.0.1"
- name: DJANGO_CSRF_TRUSTED_ORIGINS
  value: "https://<your-public-host>"
```

`settings.py` reads both (comma separated) and appends them to the defaults, so
no code change is needed.

5. Expose it and get the URL:

```bash
kubectl port-forward deployment.apps/dealership 8000:8000
```

Then use the lab's "Launch Application" / proxy URL for port 8000. That URL is
the answer to Task 24 — write it into a file named `deploymentURL` at the repo
root and commit it.

6. Create the admin and demo users in the deployed pod:

```bash
kubectl exec -it deployment.apps/dealership -- python manage.py migrate
kubectl exec -it deployment.apps/dealership -- python manage.py createsuperuser
```

The SQLite database lives in the container filesystem, so it does **not** persist
across pod restarts. Create the users, then take the screenshots in one session.

## Screenshots to capture (Tasks 25–28)

Each must show the deployment URL in the browser address bar, matching
`deploymentURL` exactly.

| File | Where | Must show |
|---|---|---|
| `deployed_landingpage` | `/` | landing page, deployment URL in address bar |
| `deployed_loggedin` | `/dealers` after login | the logged-in **username** visible |
| `deployed_dealer_detail` | `/dealer/15` | dealer details and its reviews |
| `deployed_add_review` | `/dealer/15` after posting | your new review visible |

Dealer 15 (Tempsoft, San Antonio) already has 3 seed reviews, so it is the
easiest dealer to demonstrate both the detail page and a newly added review.

## If the dealer table is empty

Work outward from Django, the same order used to verify this locally:

```bash
# 1. Is Express reachable from inside the Django pod?
kubectl exec -it deployment.apps/dealership -- python -c \
  "import os,requests; u=os.getenv('backend_url'); print(u); print(requests.get(u+'/fetchDealers').json()[:1])"

# 2. Is the sentiment service reachable?
curl "https://<code-engine-url>/analyze/Great"

# 3. What does Django itself return?
curl "<deployment-url>/djangoapp/get_dealers"
```

A `{"status": 200, "dealers": null}` response means `backend_url` is wrong —
Django reached its own view fine but could not reach Express.
