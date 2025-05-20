import os
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import get_resolver
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache  # NEW: import cache

from nlp_processing.entity_network_from_filedata import EntityNetworkPipeline
from utils.csv_utils import convert_string_to_dataframe
from utils.django_utils import get_all_url_patterns
from .serializers import FileUploadSerializer
from django.conf import settings


class FileUploadView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'progress_bar.html')

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            txt_file = serializer.validated_data['txt_file']
            csv_file = serializer.validated_data['csv_file']
            # Here, you could save or process the files as needed
            return Response({"message": "Files uploaded successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def upload_form(request):
    form_location = os.path.join(settings.BASE_DIR, 'static', 'upload_component.html')
    print(form_location)
    with open(form_location, 'r') as file:
        return HttpResponse(file.read())


@csrf_exempt
def upload_books(request):
    # Instead of saving progress to the session, we save it to the cache.
    def save_progress(progress):
        cache.set(f'upload_progress_{request.session.session_key}', progress)

    if request.method == 'POST':
        dict_data = request.POST.dict()
        csv_data = {key: value for key, value in dict_data.items() if key.startswith('csv_')}
        txt_data = {key: value for key, value in dict_data.items() if key.startswith('txt_')}
        txt_filename = txt_data["txt_filename"]
        csv_content: pd.DataFrame = convert_string_to_dataframe(csv_data["csv_contents"])
        txt_content: str = txt_data["txt_contents"]
        print("Starting entity processing...")
        entity_processor = EntityNetworkPipeline(progress_callback=save_progress)
        entity_processor.setup(text_data=txt_content, character_table=csv_content, book_filename=txt_filename)
        entity_processor.analyze_pipeline()
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def progress_update_view(request):
    if request.method == 'POST':
        # Retrieve progress from the cache.
        progress = cache.get(f'upload_progress_{request.session.session_key}', 0)
        return JsonResponse({'progress': progress})
    else:
        return HttpResponse(status=405)


def home(request):
    return HttpResponse("Hello, World!")


def entry_page(request):
    urlconf = get_all_url_patterns(get_resolver(None).url_patterns)
    endpoints = [pattern for pattern in urlconf if pattern]
    return render(request, 'entry_page.html', {'endpoints': endpoints})


def api_overview(request):
    return JsonResponse({"message": "API Overview"})
