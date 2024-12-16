# daospace/urls.py

from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),  # Include URLs from app
    path('health/', health_check, name='health_check'),
]