# Capstone Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Satisfy all 28 rubric tasks of the xrwvm fullstack capstone with genuine,
reproducible artifacts committed to the public fork.

**Architecture:** Three local processes — Django (:8000, native venv) fronting an
Express+Mongo service (:3030, docker-compose) and a Flask sentiment service (:5050,
native venv). Django's `restapis.py` is the only integration seam; it reads both
downstream URLs from `.env`, which is what lets identical code run locally and in
the Kubernetes deployment.

**Tech Stack:** Django 5.x, React 18 + react-router 6, Express 4 + Mongoose 8,
MongoDB, Flask + nltk VADER, GitHub Actions, Docker.

**Spec:** `docs/superpowers/specs/2026-08-17-capstone-build-design.md`

## Global Constraints

- Fork name must stay `xrwvm-fullstack_developer_capstone`; owner `rahmanazhar`.
- Django serves on **:8000**. Every artifact URL uses `localhost:8000`.
- `.env`: `backend_url=http://localhost:3030`, `sentiment_analyzer_url=http://localhost:5050/`
- Superuser username is **`root`**. Its password is never written to any committed file.
- Every rubric artifact lands at **repo root**, exact lowercase/camelCase names:
  `django_server`, `loginuser`, `logoutuser`, `getdealerreviews`, `getalldealers`,
  `getdealerbyid`, `getdealersbyState`, `getallcarmakes`, `analyzereview`, `CICD`,
  `deploymentURL`.
- Screenshots are PNG at repo root; Tasks 18, 19, 20, 22, 25–28 require the browser
  **address bar visible**, so capture full-window, not viewport.
- Dealer **15** is the canonical reviewed dealer (3 reviews). Kansas has exactly one
  dealer, **id 8**.
- Do not rewrite `Dealers.jsx`, `Dealer.jsx`, `PostReview.jsx`, `Login.jsx`,
  `Header.jsx` — they are complete and define the API contract.
- Never hand-write a file that is supposed to be captured program output.

---

## Task 1: Environment boot + README (rubric 1, 2)

**Files:**
- Modify: `README.md`
- Create: `server/.venv/` (not committed), `django_server`
- Modify: `.gitignore` (add `.venv`, `db.sqlite3`, `frontend/build`, `node_modules`)

**Interfaces:**
- Produces: a running Django dev server on :8000; `python`/`pip` inside `server/.venv`.

- [ ] **Step 1: Create venv and install**

```powershell
cd C:\Users\Rahman\xrwvm-fullstack_developer_capstone\server
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\pip.exe freeze
```

Record resolved versions — they go in the `django_server` artifact.

- [ ] **Step 2: Build the React frontend**

```powershell
cd server\frontend
npm install
npm run build
```

Expected: `frontend/build/index.html` exists. This must happen before Task 3,
because `settings.py` will point `TEMPLATES.DIRS` at `frontend/build`.

- [ ] **Step 3: Wire settings.py for static + templates**

Replace the empty lists at `server/djangoproj/settings.py:31`, `:61-75`, `:137`:

```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
```

```python
'DIRS': [
    os.path.join(BASE_DIR, 'frontend/static'),
    os.path.join(BASE_DIR, 'frontend/build'),
    os.path.join(BASE_DIR, 'frontend/build/static'),
],
```

```python
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend/build'),
    os.path.join(BASE_DIR, 'frontend/build/static'),
]
```

- [ ] **Step 4: Migrate and create the root superuser**

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
```

Create `root` non-interactively so no password reaches the shell history of a
committed file:

```powershell
$env:DJANGO_SUPERUSER_PASSWORD='<chosen>'
.\.venv\Scripts\python.exe manage.py createsuperuser --noinput --username root --email hazhar@coevolve.com
```

- [ ] **Step 5: Run the server and capture the artifact**

Run `manage.py runserver` in the background, then confirm with an independent
route — re-deriving "it works" from HTTP rather than from the absence of a
traceback:

```powershell
curl.exe -s -o NUL -w "%{http_code}" http://localhost:8000/
```

Expected: `200`. Write the real terminal output (version banner, watchman lines,
request log) to `django_server`.

- [ ] **Step 6: README**

Replace `# coding-project-template` with the project name, a short description,
the local-run steps, and the three-service topology. This file's public URL is
rubric Task 1's answer.

- [ ] **Step 7: Commit**

```bash
git add README.md .gitignore server/djangoproj/settings.py django_server
git commit -m "feat: boot Django, wire static/template dirs, add README"
```

---

## Task 2: About Us and Contact Us pages (rubric 3, 4)

**Files:**
- Modify: `server/frontend/static/About.html`
- Create: `server/frontend/static/Contact.html`
- Modify: `server/djangoproj/urls.py`

**Interfaces:**
- Consumes: `STATIC_URL` + `TEMPLATES.DIRS` from Task 1.
- Produces: routes `/about` and `/contact`.

- [ ] **Step 1: Add the two template routes**

In `server/djangoproj/urls.py` `urlpatterns`, after the `''` Home route:

```python
path('about/', TemplateView.as_view(template_name="About.html")),
path('contact/', TemplateView.as_view(template_name="Contact.html")),
```

- [ ] **Step 2: Fix About.html's missing CSS links**

`About.html:3` is an empty `<!-- Link the style sheet here -->`. Insert:

```html
<link rel="stylesheet" href="/static/bootstrap.min.css">
<link rel="stylesheet" href="/static/style.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>About Us | Best Cars Dealerships</title>
```

- [ ] **Step 3: Replace the three placeholder person cards**

Requirements from the rubric, all four of which must be present per card:
realistic image, name, role, brief detail, email ID. Use **fictional** identities
with `randomuser.me` portraits and emails on the app's own domain. Fill the
`about-header` banner div with a company blurb.

- [ ] **Step 4: Create Contact.html**

Same shell as About.html, with the nav `active` class moved to the **Contact Us**
`<a>` (rubric names this explicitly) and `Home`/`About Us` left inactive. Include
address, phone, email, business hours, and the shipped `contactus.png` image.

- [ ] **Step 5: Verify in a real browser**

Navigate to `http://localhost:8000/about` and `/contact`. Failure condition:
unstyled text (CSS 404) or a broken portrait. Check the network panel for 404s
rather than trusting that the page "looks fine".

- [ ] **Step 6: Commit**

```bash
git add server/frontend/static/About.html server/frontend/static/Contact.html server/djangoproj/urls.py
git commit -m "feat: add About Us content and Contact Us page"
```

---

## Task 3: Auth views, registration, React routes (rubric 5, 6, 7)

**Files:**
- Modify: `server/djangoapp/views.py`, `server/djangoapp/urls.py`
- Create: `server/frontend/src/components/Register/Register.jsx`
- Modify: `server/frontend/src/App.js`, `server/djangoproj/urls.py`
- Create: `loginuser`, `logoutuser`

**Interfaces:**
- Produces:
  - `login_user(request)` → `{"userName": str, "status": "Authenticated"}` (exists)
  - `logout_request(request)` → `{"userName": ""}`
  - `registration(request)` → `{"userName": str, "status": "Authenticated"}` or
    `{"userName": str, "error": "Already Registered"}`

- [ ] **Step 1: Add logout and registration views**

```python
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        logger.debug("%s is new user", username)
    if not username_exist:
        user = User.objects.create_user(
            username=username, first_name=first_name, last_name=last_name,
            password=password, email=email)
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    return JsonResponse({"userName": username, "error": "Already Registered"})
```

Uncomment the `User` and `logout` imports at the top of the file.

- [ ] **Step 2: Register the URLs**

`server/djangoapp/urls.py`:

```python
path(route='login', view=views.login_user, name='login'),
path(route='logout', view=views.logout_request, name='logout'),
path(route='register', view=views.registration, name='register'),
```

- [ ] **Step 3: Create Register.jsx**

Must contain all five inputs — Username, First Name, Last Name, Email, Password —
plus a Register button (rubric enumerates them). POST to
`window.location.origin+"/djangoapp/register"` with keys `userName`, `password`,
`firstName`, `lastName`, `email`, matching Step 1's view exactly. On
`status === "Authenticated"`, store `username` in `sessionStorage` and redirect to
`/`. Import `./Register.css`, which already exists.

- [ ] **Step 4: Add the React routes**

`server/frontend/src/App.js`:

```jsx
<Route path="/register" element={<Register />} />
<Route path="/dealers" element={<Dealers />} />
<Route path="/dealer/:id" element={<Dealer />} />
<Route path="/postreview/:id" element={<PostReview />} />
```

And in `server/djangoproj/urls.py`, serve `index.html` for each so a hard refresh
does not 404:

```python
path('login/', TemplateView.as_view(template_name="index.html")),
path('register/', TemplateView.as_view(template_name="index.html")),
path('dealers/', TemplateView.as_view(template_name="index.html")),
path('dealer/<int:dealer_id>', TemplateView.as_view(template_name="index.html")),
path('postreview/<int:dealer_id>', TemplateView.as_view(template_name="index.html")),
```

- [ ] **Step 5: Rebuild the frontend**

`npm run build` — the Django template dirs read from `build/`, so unbuilt JSX
changes are invisible. This is the single most common false failure in this stack.

- [ ] **Step 6: Capture the login/logout artifacts**

```powershell
curl.exe -i -X POST http://localhost:8000/djangoapp/login `
  -H "Content-Type: application/json" `
  -d "{\"userName\":\"root\",\"password\":\"<pw>\"}" `
  -c cookies.txt
curl.exe -i -X GET http://localhost:8000/djangoapp/logout -b cookies.txt
```

Failure condition for the login check: response lacks `"status": "Authenticated"`.
Write command + real output to `loginuser` and `logoutuser`. Redact the password
in the committed file, keeping the output verbatim.

- [ ] **Step 7: Commit**

```bash
git add server/djangoapp/views.py server/djangoapp/urls.py server/djangoproj/urls.py \
        server/frontend/src/App.js server/frontend/src/components/Register/Register.jsx \
        loginuser logoutuser
git commit -m "feat: add logout/registration views, Register page, SPA routes"
```

---

## Task 4: Express/Mongo dealer routes (rubric 8, 9, 10, 11)

**Files:**
- Modify: `server/database/app.js:59-72`
- Create: `getdealerreviews`, `getalldealers`, `getdealerbyid`, `getdealersbyState`

**Interfaces:**
- Produces: `GET /fetchDealers`, `GET /fetchDealers/:state`, `GET /fetchDealer/:id`
  on `localhost:3030`, each returning a JSON array.

- [ ] **Step 1: Implement the three stubbed routes**

```javascript
app.get('/fetchDealers', async (req, res) => {
  try {
    const documents = await Dealerships.find();
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const documents = await Dealerships.find({ state: req.params.state });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const documents = await Dealerships.find({ id: req.params.id });
    res.json(documents);
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});
```

`/fetchDealer/:id` returns an **array**, which is what `Dealer.jsx` expects when
it calls `Array.from(retobj.dealer)`.

- [ ] **Step 2: Build the image, then start compose**

`docker-compose.yml` declares `image: nodeapp` with no `build:` key, so compose
alone fails on a missing image:

```powershell
cd server\database
docker build -t nodeapp .
docker compose up -d
docker compose ps
```

- [ ] **Step 3: Verify seeding actually happened**

```powershell
curl.exe -s http://localhost:3030/fetchDealers | python -c "import json,sys; d=json.load(sys.stdin); print(len(d))"
```

Expected: `50`. Failure condition: `0` means `deleteMany` ran but `insertMany`
lost the race, or Mongo was not up when `app.js` started — restart `api`.

- [ ] **Step 4: Capture the four artifacts**

```powershell
curl.exe -s http://localhost:3030/fetchReviews/dealer/15   # getdealerreviews
curl.exe -s http://localhost:3030/fetchDealers             # getalldealers
curl.exe -s http://localhost:3030/fetchDealer/15           # getdealerbyid
curl.exe -s http://localhost:3030/fetchDealers/Kansas      # getdealersbyState
```

Kansas expects exactly one dealer, id 8. Write command + output to each file.

- [ ] **Step 5: Commit**

```bash
git add server/database/app.js getdealerreviews getalldealers getdealerbyid getdealersbyState
git commit -m "feat: implement Express dealer fetch routes"
```

---

## Task 5: Car models, admin, populate (rubric 12, 13, 14, 15)

**Files:**
- Modify: `server/djangoapp/models.py`, `server/djangoapp/admin.py`,
  `server/djangoapp/populate.py`, `server/djangoapp/views.py`,
  `server/djangoapp/urls.py`, `server/djangoapp/apps.py`
- Create: `getallcarmakes`, `admin_login.png`, `admin_logout.png`

**Interfaces:**
- Produces: `CarMake(name, description)`, `CarModel(car_make FK, name, type, year)`,
  and `get_cars(request)` → `{"CarModels": [{"CarModel": str, "CarMake": str}]}`.

- [ ] **Step 1: Define the models**

```python
class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class CarModel(models.Model):
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    CAR_TYPES = [(SEDAN, 'Sedan'), (SUV, 'SUV'), (WAGON, 'Wagon')]

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CAR_TYPES, default=SUV)
    year = models.IntegerField(
        default=2023,
        validators=[MaxValueValidator(2023), MinValueValidator(2015)])

    def __str__(self):
        return self.name
```

Uncomment the three imports at the top of `models.py`.

- [ ] **Step 2: Register in admin with an inline**

```python
class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1


class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ('name', 'description')


class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year')
    list_filter = ('type', 'year', 'car_make')


admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
```

The inline is what makes rubric Task 15's "Car Models from the admin page"
screenshot show models nested under their make.

- [ ] **Step 3: Write populate.py**

Replace the one-line stub with idempotent seeding — `initiate()` runs on every
app start, so a plain `create()` would duplicate rows on each reload. Seed at
least 5 makes with 2–3 models each, then guard:

```python
def initiate():
    if CarMake.objects.exists():
        return
```

- [ ] **Step 4: Call initiate() on app ready**

In `server/djangoapp/apps.py`, `DjangoappConfig.ready()` calls
`from .populate import initiate; initiate()`. Import inside the method, not at
module scope — importing models before the app registry is populated raises
`AppRegistryNotReady`.

- [ ] **Step 5: Add the get_cars view and URL**

```python
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name,
                     "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})
```

URL: `path(route='get_cars', view=views.get_cars, name='getcars')`.

- [ ] **Step 6: Migrate and capture getallcarmakes**

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations djangoapp
.\.venv\Scripts\python.exe manage.py migrate
curl.exe -s http://localhost:8000/djangoapp/get_cars
```

Failure condition: `{"CarModels": []}` — means `initiate()` never ran or the
guard short-circuited on an empty-but-existing table.

- [ ] **Step 7: Capture the two admin screenshots**

Drive a real browser: `/admin` → log in as `root` → capture `admin_login.png`
showing the authenticated admin index with CarMake/CarModel registered. Then log
out and capture `admin_logout.png` showing the "logged out" confirmation.

- [ ] **Step 8: Commit**

```bash
git add server/djangoapp/models.py server/djangoapp/admin.py server/djangoapp/populate.py \
        server/djangoapp/apps.py server/djangoapp/views.py server/djangoapp/urls.py \
        server/djangoapp/migrations getallcarmakes admin_login.png admin_logout.png
git commit -m "feat: add CarMake/CarModel, admin registration, populate seeding"
```

---

## Task 6: Sentiment analyzer service (rubric 16)

**Files:**
- Create: `analyzereview`, `~/nltk_data/sentiment/vader_lexicon.zip` (not committed)
- Modify: `server/djangoapp/restapis.py`

**Interfaces:**
- Produces: `analyze_review_sentiments(text)` → `{"sentiment": "positive"|"neutral"|"negative"}`

- [ ] **Step 1: Install and place the lexicon**

```powershell
.\.venv\Scripts\pip.exe install flask nltk
```

`SentimentIntensityAnalyzer()` is constructed at **import time**, so a missing
lexicon kills Flask at startup with `LookupError`, not on first request. Copy the
shipped `server/djangoapp/microservices/sentiment/vader_lexicon.zip` into
`$env:USERPROFILE\nltk_data\sentiment\`. Verify before starting Flask:

```powershell
.\.venv\Scripts\python.exe -c "from nltk.sentiment import SentimentIntensityAnalyzer; print(SentimentIntensityAnalyzer().polarity_scores('Fantastic services'))"
```

Expected: a dict with `compound` > 0. This check fails loudly if the lexicon is
missing — which is the point of running it separately.

- [ ] **Step 2: Start Flask on 5050**

`app.py` ends in `app.run(debug=True)` → port 5000, but `.env` expects 5050. Run
it without editing the course file:

```powershell
cd server\djangoapp\microservices
$env:FLASK_APP='app.py'
..\..\.venv\Scripts\python.exe -m flask run -p 5050
```

- [ ] **Step 3: Implement the three restapis functions**

```python
def get_request(endpoint, **kwargs):
    params = "&".join(f"{key}={value}" for key, value in kwargs.items())
    request_url = f"{backend_url}{endpoint}?{params}"
    print(f"GET from {request_url}")
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Network exception occurred: {err}")


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict)
        return response.json()
    except Exception as err:
        print(f"Network exception occurred: {err}")
```

Uncomment `import requests`.

- [ ] **Step 4: Capture analyzereview**

The rubric names the exact text — "Fantastic services":

```powershell
curl.exe -s http://localhost:5050/analyze/Fantastic%20services
```

Expected: `{"sentiment": "positive"}`. Write command + output to `analyzereview`.

- [ ] **Step 5: Commit**

```bash
git add server/djangoapp/restapis.py analyzereview
git commit -m "feat: implement restapis backend/sentiment calls"
```

---

## Task 7: Dealer views end-to-end + app screenshots (rubric 17–22)

**Files:**
- Modify: `server/djangoapp/views.py`, `server/djangoapp/urls.py`
- Create: `get_dealers.png`, `get_dealers_loggedin.png`, `dealersbystate.png`,
  `dealer_id_reviews.png`, `dealership_review_submission.png`, `added_review.png`

**Interfaces:**
- Consumes: `get_request`, `analyze_review_sentiments`, `post_review` from Task 6.
- Produces: the four dealer endpoints in the spec's contract table.

- [ ] **Step 1: Add the dealer views**

```python
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    return JsonResponse({"status": 400, "message": "Bad Request"})


@csrf_exempt
def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse({"status": 401,
                                 "message": "Error in posting review"})
    return JsonResponse({"status": 403, "message": "Unauthorized"})
```

`get_dealer_reviews` calls the sentiment service **once per review**; the
`sentiment` key exists only in this response, never in Mongo.

- [ ] **Step 2: Register the URLs**

```python
path(route='get_dealers', view=views.get_dealerships, name='get_dealers'),
path(route='get_dealers/<str:state>', view=views.get_dealerships, name='get_dealers_by_state'),
path(route='dealer/<int:dealer_id>', view=views.get_dealer_details, name='dealer_details'),
path(route='reviews/dealer/<int:dealer_id>', view=views.get_dealer_reviews, name='dealer_details'),
path(route='add_review', view=views.add_review, name='add_review'),
```

- [ ] **Step 3: Verify each endpoint before touching the browser**

```powershell
curl.exe -s http://localhost:8000/djangoapp/get_dealers | python -c "import json,sys; print(len(json.load(sys.stdin)['dealers']))"
curl.exe -s http://localhost:8000/djangoapp/reviews/dealer/15 | python -c "import json,sys; print([r['sentiment'] for r in json.load(sys.stdin)['reviews']])"
```

Expected: `50`, then three sentiment strings. Isolating this from the UI means a
blank React table later is unambiguously a frontend problem.

- [ ] **Step 4: Capture the six screenshots**

All with the address bar visible. Order matters — 21 and 22 are a before/after
pair whose details must match:

| File | Route | Must show |
|---|---|---|
| `get_dealers.png` | `/dealers` | dealer table, **not** logged in |
| `get_dealers_loggedin.png` | `/dealers` | Review Dealer column + username |
| `dealersbystate.png` | `/dealers` after state filter | filtered rows |
| `dealer_id_reviews.png` | `/dealer/15` | dealer details + 3 reviews |
| `dealership_review_submission.png` | `/postreview/15` | filled form, pre-submit |
| `added_review.png` | `/dealer/15` | the new review, matching the previous shot |

- [ ] **Step 5: Commit**

```bash
git add server/djangoapp/views.py server/djangoapp/urls.py *.png
git commit -m "feat: add dealer/review views with sentiment enrichment"
```

---

## Task 8: CI/CD workflow (rubric 23)

**Files:**
- Create: `.github/workflows/main.yml`, `.jshintrc`, `CICD`

- [ ] **Step 1: Write the workflow**

```yaml
name: 'Lint Code'
on: push
jobs:
  lint_python:
    name: Lint Python Files
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install flake8
      - name: Lint with flake8
        run: |
          find . -name "*.py" -exec flake8 --ignore=E501,F401 {} +
  lint_js:
    name: Lint JS Files
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install jshint --global
      - name: Lint with jshint
        run: |
          find . -name "*.js" -not -path "*/node_modules/*" -not -path "*/build/*" -exec jshint --config .jshintrc {} +
```

- [ ] **Step 2: Add .jshintrc**

`app.js` uses `async`/`await` and an implicit global (`data =` at line 76), so
jshint needs `"esversion": 11` and `"node": true` or the run fails on course code.

- [ ] **Step 3: Push and watch the real run**

```powershell
git push origin main
gh run watch
gh run view --log
```

Failure condition: conclusion `failure`. Fix lint errors and re-push — do not
weaken the config to force a pass beyond the flake8 ignores above.

- [ ] **Step 4: Capture CICD**

Write the genuine `gh run view --log` output, showing both jobs' steps, to `CICD`.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/main.yml .jshintrc CICD
git commit -m "ci: add flake8 and jshint linting workflow"
```

---

## Task 9: Deployment runbook (rubric 24–28)

**Files:**
- Create: `LAB_DEPLOY.md`, `server/Dockerfile`, `server/deployment.yaml`,
  `deploymentURL` (user fills)

- [ ] **Step 1: Add the Django Dockerfile**

```dockerfile
FROM python:3.12.0-slim-bookworm
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP=/app
WORKDIR $APP
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . $APP
EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "djangoproj.wsgi"]
```

- [ ] **Step 2: Add deployment.yaml**

A `Deployment` + `Service` pair for `dealership` on port 8000, image referencing
the lab's ICR namespace.

- [ ] **Step 3: Write LAB_DEPLOY.md**

Exact copy-paste sequence for the Skills Network lab: deploy the sentiment
microservice to Code Engine, capture its public URL into `.env`, build and push
the Django image to ICR, apply the deployment, expose it, then read the route.
Include the four screenshots to capture and the `deploymentURL` file to write.

- [ ] **Step 4: Commit**

```bash
git add server/Dockerfile server/deployment.yaml LAB_DEPLOY.md
git commit -m "feat: add deployment manifests and lab runbook"
```

- [ ] **Step 5: Hand off** — user executes in the lab and commits
  `deploymentURL` + the four `deployed_*.png` files.

---

## Self-Review

**Spec coverage:** All 9 spec phases map to Tasks 1–9 here; all 28 rubric tasks are
claimed by exactly one task. Spec §6 content decisions land in Task 2 Step 3. Spec
§8 risks each have a mitigating step: nltk → Task 6 Step 1; unpinned Django → Task 1
Step 1/5; missing compose build → Task 4 Step 2; unverifiable deploy → Task 9.

**Placeholder scan:** No TBD/TODO. Two places intentionally specify requirements
rather than literal code — Task 2 Step 3/4 (HTML content) and Task 3 Step 3
(Register.jsx) — because the rubric enumerates the required elements and those are
the acceptance criteria. Every code-carrying step has real code.

**Type consistency:** `get_dealerships` is used for both `get_dealers` and
`get_dealers/<state>` via its `state="All"` default, matching `Dealers.jsx`'s
`"All"` option value. `get_cars` returns `CarModels` with `CarModel`/`CarMake` keys
exactly as `PostReview.jsx` reads them. `registration` accepts the same five keys
Register.jsx sends. `/fetchDealer/:id` returns an array, matching
`Array.from(retobj.dealer)`.
