"""
URL configuration for Expense_Tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home, login_view, fraud_alerts, track_expenses, export_reports

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', home, name='home'),  # Landing page (landing_page.html)
    path('login/', login_view, name='login'),  # Login page (login.html)
    path('fraud-alerts/', fraud_alerts, name='fraud_alerts'),  # Fraud alerts page
    path('track_expenses/', track_expenses, name='track_expenses'),  # Track expenses (base.html or another dashboard)
    path('export-reports/', export_reports, name='export_reports'),
    path('accounts/', include('accounts.urls')),  # If you have an accounts app
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
