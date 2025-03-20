from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),  # Home page
    path("Fraud-Alerts/", include("Fraud_Alerts.urls")),  # Fraud Alerts page

]
