import os

import httpx
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CarEvaluationForm, RegisterForm
from .models import CarEvaluation


FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8001/predict")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("predict_car")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("predict_car")
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("predict_car")


@login_required
def dashboard(request):
    evaluations = CarEvaluation.objects.filter(user=request.user)
    return render(request, "prediction/dashboard.html", {
        "total_evaluations": evaluations.count(),
        "unacceptable_count": evaluations.filter(prediction="Unacceptable").count(),
        "acceptable_count": evaluations.filter(prediction="Acceptable").count(),
        "good_count": evaluations.filter(prediction="Good").count(),
        "very_good_count": evaluations.filter(prediction="Very Good").count(),
        "latest_evaluation": evaluations.first(),
        "recent_evaluations": evaluations[:5],
    })


@login_required
def prediction_history(request):
    evaluations = CarEvaluation.objects.filter(user=request.user)
    return render(request, "prediction/history.html", {"evaluations": evaluations})


def predict_car(request):
    result = None
    submitted = None
    submitted_display = None
    error = None
    form = CarEvaluationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        submitted = form.cleaned_data
        submitted_display = {
            name: dict(form.fields[name].choices)[value]
            for name, value in submitted.items()
        }
        try:
            response = httpx.post(FASTAPI_URL, json=submitted, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            if result.get("prediction") not in dict(CarEvaluation._meta.get_field("prediction").choices):
                raise ValueError("Unexpected prediction response")

            CarEvaluation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                **submitted,
                prediction=result["prediction"],
                confidence=result.get("confidence"),
            )
        except httpx.RequestError:
            error = "The evaluation service is currently unavailable. Please try again shortly."
        except httpx.HTTPStatusError:
            error = "The evaluation service could not process those details. Please review them and try again."
        except (ValueError, KeyError, TypeError):
            error = "The evaluation service returned an invalid response. Please try again."

    return render(request, "prediction/predict.html", {
        "form": form,
        "result": result,
        "submitted": submitted,
        "submitted_display": submitted_display,
        "error": error,
    })
