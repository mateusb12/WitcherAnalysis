import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import get_resolver
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from utils.django_utils import get_all_url_patterns
from .serializers import FileUploadSerializer
from django.conf import settings


class FileUploadView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'upload_form.html')

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            # Retrieve the uploaded files using serializer.validated_data
            txt_file = serializer.validated_data['txt_file']
            csv_file = serializer.validated_data['csv_file']

            # Here, you can now handle the files, such as saving them or processing them
            # For example:
            # with open(txt_file.name, 'wb+') as destination:
            #     for chunk in txt_file.chunks():
            #         destination.write(chunk)

            return Response({"message": "Files uploaded successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def upload_form(request):
    form_location = os.path.join(settings.BASE_DIR, 'static', 'upload_component.html')
    print(form_location)
    with open(form_location, 'r') as file:
        return HttpResponse(file.read())


def home(request):
    return HttpResponse("Hello, World!")


def entry_page(request):
    urlconf = get_all_url_patterns(get_resolver(None).url_patterns)
    endpoints = [pattern for pattern in urlconf if pattern]
    return render(request, 'entry_page.html', {'endpoints': endpoints})


def api_overview(request):
    return JsonResponse({"message": "API Overview"})
