from django.urls import path

from . import views
from .views import FileUploadView, upload_form

urlpatterns = [
    path('', views.api_overview, name='api-overview'),
    path('form/', upload_form, name='upload-form'),
]
