# Deployment Runbook (Skills Network Lab)

Tasks 1–23 were built and verified locally. This runbook covers the five
artifacts that can only be produced inside the IBM Cloud lab: `deploymentURL`,
`deployed_landingpage`, `deployed_loggedin`, `deployed_dealer_detail`,
`deployed_add_review`.

## Confidence note

| Part | Status |
|---|---|
| App code, Dockerfiles, both `deployment.yaml` files, env-var wiring | **Verified locally** |
| `ibmcloud` / `kubectl` command syntax and the lab proxy URL scheme | **Not verifiable outside the lab** — if a command differs from your lab sheet, the lab sheet wins |

## Architecture in the cluster

```
Browser ──▶ dealership (Django, :8000) ──┬──▶ dealership-api (Express, :3030) ──▶ mongo-db (:27017)
                                         └──▶ sentianalyzer (Flask, Code Engine)
```

Four env vars carry the wiring. Get them wrong and the failure is **silent** — a
blank dealer table, no error page:

| Var | Value | Trap |
|---|---|---|
| `backend_url` | `http://dealership-api:3030` | **no** trailing slash |
| `sentiment_analyzer_url` | Code Engine URL | **must** end in `/` |
| `MONGO_URL` (api container) | `mongodb://mongo-db:27017/` | see below |
| `DJANGO_ALLOWED_HOSTS` | your public host | omit it and Django 400s |

**Why `MONGO_URL` exists:** `app.js` defaults to `mongodb://mongo_db:27017/`,
the docker-compose service name. Kubernetes Service names cannot contain
underscores, so no valid Service could ever answer that hostname. The api
container overrides it to reach the `mongo-db` Service instead. Local
docker-compose runs are unaffected — the default still applies there.

## Step 0 — Get the repo into the lab (do this first)

Every other step depends on it. The lab home directory does not have your fork
until you clone it.

```bash
cd ~
[ -d xrwvm-fullstack_developer_capstone ] \
  || git clone https://github.com/rahmanazhar/xrwvm-fullstack_developer_capstone.git
cd xrwvm-fullstack_developer_capstone
git pull --ff-only
export REPO=$(pwd)

# Confirm the three build inputs exist before going further.
ls -l server/djangoapp/microservices/Dockerfile server/Dockerfile \
      server/deployment.yaml server/database/deployment.yaml
echo "namespace: $SN_ICR_NAMESPACE"
```

If `$SN_ICR_NAMESPACE` is empty, stop — nothing below will push correctly.

## Step 1 — IBM Cloud context

`ibmcloud ce` fails with *"No resource group targeted"* until a group is
targeted. **Look the name up rather than assuming it** — lab accounts often have
no group called `Default`, and no group flagged as the default, so it must be
passed explicitly:

```bash
ibmcloud resource groups
```

```
Name         ID                                 Default Group   State
production   d9bc65f89412482cb207f045f74ba87f   false           ACTIVE
```

Then target that name (it was `production` on this account, not `Default`):

```bash
ibmcloud target -g production
```

**Do not create a Code Engine project.** The lab provisions one for you and the
lab ServiceId is not authorized to create more — `ce project create` fails with
*"This action is forbidden."* List what already exists and select it:

```bash
ibmcloud ce project list
```

```
Name                                ID                                    Status  Region
Code Engine - sn-labs-rahmanprojec  d4a867f1-3a73-4690-addd-04f2ed37b5f7  active  us-south
```

The provisioned name contains spaces, so select it by ID:

```bash
ibmcloud ce project select --id <the-id-from-the-list>
ibmcloud ce project current
```

Until a project is selected, every `ce application` call fails with *"No project
selected."*

Note the error message's own suggestion, `ibmcloud target -g
RESOURCE_GROUP_NAME`, is a placeholder — passing it literally fails with
*"Could not get resource group"*.

## Step 2 — Sentiment analyzer to Code Engine

```bash
cd $REPO/server/djangoapp/microservices
docker build -t us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer .
docker push us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer

ibmcloud ce application create \
  --name sentianalyzer \
  --image us.icr.io/$SN_ICR_NAMESPACE/senti_analyzer \
  --registry-secret icr-secret \
  --port 5000

ibmcloud ce application get --name sentianalyzer --output url
```

**Port 5000, not 5050.** `microservices/Dockerfile` runs `flask run
--host=0.0.0.0` on Flask's default port; 5050 is only the local convention.

Verify, then save the URL **with a trailing slash**:

```bash
export SENTI_URL="https://<paste-code-engine-host>/"
curl "${SENTI_URL}analyze/Fantastic%20services"
# expect: {"sentiment": "positive"}
```

A 500 here means the VADER lexicon is missing in the image — see README.

## Step 3 — MongoDB + Express API to Kubernetes

```bash
cd $REPO/server/database
docker build -t us.icr.io/$SN_ICR_NAMESPACE/dealership-api .
docker push us.icr.io/$SN_ICR_NAMESPACE/dealership-api

sed -i "s|<NAMESPACE>|$SN_ICR_NAMESPACE|g" deployment.yaml
kubectl apply -f deployment.yaml
kubectl get pods -w      # wait for both mongo-db and dealership-api to be Running
```

Confirm the API seeded 50 dealerships before moving on:

```bash
kubectl exec deployment.apps/dealership-api -- \
  sh -c "wget -qO- http://localhost:3030/fetchDealers | head -c 120"
```

Note `app.js` wipes and re-seeds on **every start**, so restarting this pod
erases posted reviews. Capture `deployed_add_review` without restarting it.

## Step 4 — Django to Kubernetes

```bash
cd $REPO/server
docker build -t us.icr.io/$SN_ICR_NAMESPACE/dealership .
docker push us.icr.io/$SN_ICR_NAMESPACE/dealership

sed -i "s|<NAMESPACE>|$SN_ICR_NAMESPACE|g" deployment.yaml
sed -i "s|https://sentiment-analyzer.REPLACE_ME.codeengine.appdomain.cloud/|$SENTI_URL|" deployment.yaml
grep -A2 -E "image:|sentiment_analyzer_url|backend_url" deployment.yaml   # eyeball it

kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs deployment.apps/dealership
```

Then allow the public hostname. Django rejects unknown hosts with a 400
`DisallowedHost`, which looks exactly like a broken deployment:

```bash
kubectl set env deployment/dealership \
  DJANGO_ALLOWED_HOSTS="<your-public-host>,localhost,127.0.0.1" \
  DJANGO_CSRF_TRUSTED_ORIGINS="https://<your-public-host>"
```

`settings.py` reads both (comma separated) and appends them to the defaults, so
no code change is needed.

## Step 5 — Expose it and create users

```bash
kubectl port-forward deployment.apps/dealership 8000:8000
```

Use the lab's **Launch Application** on port 8000. That URL is Task 24 — write
it into `deploymentURL` at the repo root, replacing the placeholder.

The container's SQLite database does not survive a pod restart, so create the
users and take all four screenshots in one session:

```bash
kubectl exec -it deployment.apps/dealership -- python manage.py migrate
kubectl exec -it deployment.apps/dealership -- python manage.py createsuperuser
```

## Screenshots (Tasks 25–28)

Each must show the deployment URL in the address bar, matching `deploymentURL`.

| File | Where | Must show |
|---|---|---|
| `deployed_landingpage` | `/` | landing page |
| `deployed_loggedin` | `/dealers` after login | the logged-in **username** |
| `deployed_dealer_detail` | `/dealer/15` | dealer details and reviews |
| `deployed_add_review` | `/dealer/15` after posting | your new review |

Dealer 15 (Tempsoft, San Antonio) ships with 3 seed reviews, so it demonstrates
both the detail page and a newly added one.

## If the dealer table is blank

Work outward from Django, the order used to verify this locally:

```bash
# 1. Can Django reach Express in-cluster?
kubectl exec deployment.apps/dealership -- python -c \
  "import os,requests; u=os.getenv('backend_url'); print(u, requests.get(u+'/fetchDealers').json()[:1])"

# 2. Can Express reach Mongo?
kubectl logs deployment.apps/dealership-api | head -20

# 3. Is the sentiment service up?
curl "${SENTI_URL}analyze/Great"

# 4. What does Django return?
curl "<deployment-url>/djangoapp/get_dealers"
```

`{"status": 200, "dealers": null}` means `backend_url` is wrong — Django's own
view ran fine but could not reach Express.
