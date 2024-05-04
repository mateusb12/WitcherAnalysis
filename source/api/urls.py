from django.urls import path
from .views import FileUploadView, upload_form

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('form/', upload_form, name='upload-form'),
]
