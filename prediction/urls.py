from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path("", views.predict_car, name="predict_car"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("history/", views.prediction_history, name="prediction_history"),
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
