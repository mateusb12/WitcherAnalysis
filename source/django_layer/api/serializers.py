from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    txt_file = serializers.FileField()
    csv_file = serializers.FileField()
