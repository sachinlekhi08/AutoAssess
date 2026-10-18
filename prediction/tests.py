from unittest.mock import Mock, patch

import httpx
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import CarEvaluationForm
from .models import CarEvaluation


SAMPLE = {"buying": "low", "maint": "med", "doors": "4", "persons": "4", "lug_boot": "big", "safety": "high"}


class AuthenticationTests(TestCase):
    def test_user_can_register_and_is_logged_in(self):
        response = self.client.post(reverse("register"), {
            "username": "testuser", "email": "test@example.com",
            "password1": "StrongPassword123!", "password2": "StrongPassword123!",
        })
        self.assertRedirects(response, reverse("predict_car"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="testuser").pk)

    def test_login_and_logout(self):
        User.objects.create_user(username="driver", password="TestPassword123!")
        response = self.client.post(reverse("login"), {"username": "driver", "password": "TestPassword123!"})
        self.assertRedirects(response, reverse("predict_car"))
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("predict_car"))


class ValidationTests(TestCase):
    def test_all_fields_render_as_selects(self):
        form = CarEvaluationForm()
        self.assertTrue(all(field.widget.input_type == "select" for field in form.fields.values()))

    def test_invalid_category_is_rejected(self):
        form = CarEvaluationForm({**SAMPLE, "doors": "six"})
        self.assertFalse(form.is_valid())
        self.assertIn("doors", form.errors)


class ProtectedPageTests(TestCase):
    def test_history_and_dashboard_require_login(self):
        for name in ("prediction_history", "dashboard"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login/", response.url)


class UserDataTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="TestPassword123!")
        self.user2 = User.objects.create_user(username="user2", password="TestPassword123!")
        CarEvaluation.objects.create(user=self.user1, **SAMPLE, prediction="Very Good", confidence=91.5)
        CarEvaluation.objects.create(user=self.user2, **SAMPLE, prediction="Unacceptable", confidence=88.0)

    def test_user_sees_only_own_history(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("prediction_history"))
        self.assertEqual(list(response.context["evaluations"]), list(CarEvaluation.objects.filter(user=self.user1)))

    def test_dashboard_statistics(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["total_evaluations"], 1)
        self.assertEqual(response.context["very_good_count"], 1)
        self.assertEqual(response.context["unacceptable_count"], 0)


class PredictionFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="evaluator", password="TestPassword123!")
        self.client.force_login(self.user)

    @patch("prediction.views.httpx.post")
    def test_valid_prediction_is_saved_and_displayed(self, mock_post):
        mock_post.return_value = Mock(
            raise_for_status=Mock(),
            json=Mock(return_value={
                "prediction": "Very Good", "confidence": 92.5,
                "probabilities": {"Unacceptable": 1.0, "Acceptable": 2.0, "Good": 4.5, "Very Good": 92.5},
            }),
        )
        response = self.client.post(reverse("predict_car"), SAMPLE)
        self.assertContains(response, "Very Good")
        evaluation = CarEvaluation.objects.get(user=self.user)
        self.assertEqual(evaluation.prediction, "Very Good")
        self.assertEqual(evaluation.buying, "low")
        mock_post.assert_called_once_with("http://127.0.0.1:8001/predict", json=SAMPLE, timeout=60.0)

    @patch("prediction.views.httpx.post", side_effect=httpx.ConnectError("offline"))
    def test_unavailable_service_shows_safe_error(self, _mock_post):
        response = self.client.post(reverse("predict_car"), SAMPLE)
        self.assertContains(response, "currently unavailable")
        self.assertFalse(CarEvaluation.objects.filter(user=self.user).exists())
