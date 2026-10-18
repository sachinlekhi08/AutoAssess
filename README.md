# AutoAssess — Car Evaluation Prediction System

AutoAssess is a Django application backed by a separate FastAPI inference service and a saved Scikit-learn pipeline. It classifies a categorical vehicle profile as **Unacceptable**, **Acceptable**, **Good**, or **Very Good**. Signed-in users receive a private dashboard and evaluation history.

> AutoAssess is an academic classification system. Its output is not professional automotive, safety, or purchasing advice.

## Architecture

```text
Browser → Django form validation → FastAPI `/predict`
                                      ↓
                          saved Scikit-learn pipeline
                                      ↓
Browser ← result + saved history ← Django database
```

- `car_evaluation/`: Django project settings and root routing
- `prediction/`: forms, views, database model, admin, routes, migrations, and tests
- `api/`: FastAPI inference service and API tests
- `ml/car_evaluation_model.pkl`: fitted preprocessing and Random Forest pipeline
- `templates/`: evaluation, authentication, dashboard, and history pages
- `static/`: responsive AutoAssess interface assets

The existing Django authentication, environment-based database configuration, WhiteNoise static handling, and HTTP service boundary remain intact.

## Model contract

The model receives a pandas DataFrame with these exact columns:

| Field | Accepted values |
| --- | --- |
| `buying` | `vhigh`, `high`, `med`, `low` |
| `maint` | `vhigh`, `high`, `med`, `low` |
| `doors` | `2`, `3`, `4`, `5more` |
| `persons` | `2`, `4`, `more` |
| `lug_boot` | `small`, `med`, `big` |
| `safety` | `low`, `med`, `high` |

No manual category encoding occurs in Django or FastAPI. The fitted pipeline owns preprocessing. FastAPI validates the raw categories, maps the four model outputs to readable labels, and returns per-class probabilities when available.

## Local setup

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
uv run python manage.py migrate
```

Set a real `DJANGO_SECRET_KEY` in `.env`, then start both services in separate terminals:

```bash
uv run uvicorn api.main:app --host 127.0.0.1 --port 8001
uv run python manage.py runserver
```

Open `http://127.0.0.1:8000/`. FastAPI documentation is available at `http://127.0.0.1:8001/docs`.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Required Django secret |
| `DJANGO_DEBUG` | Use `True` only for local development |
| `DATABASE_URL` | Optional hosted database URL; SQLite is the local default |
| `FASTAPI_URL` | Inference endpoint; defaults to `http://127.0.0.1:8001/predict` |
| `RENDER_EXTERNAL_HOSTNAME` | Added to Django allowed hosts when supplied |

## Tests and checks

```bash
uv run pytest
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

The test suite covers registration, login/logout, protected pages, dropdown validation, user-specific history, dashboard counts, all three supplied inference samples, rejected API categories, service failure handling, and the Django-to-FastAPI persistence flow.

## Deployment

The existing `build.sh` installs locked dependencies, collects static assets, and applies migrations. Example start commands:

```bash
# Django web service
uv run gunicorn car_evaluation.wsgi:application --bind 0.0.0.0:$PORT

# FastAPI inference service
uv run uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Configure `FASTAPI_URL` on the web service with the deployed inference service `/predict` URL. The model file must remain at `ml/car_evaluation_model.pkl` in both local and deployed builds.
