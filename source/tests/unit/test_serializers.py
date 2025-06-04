import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_layer.project_config')

if not settings.configured:
    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "rest_framework",
        ],
        SITE_ID=1,
        MIDDLEWARE_CLASSES=(),
    )

django.setup()

from django_layer.api.serializers import FileUploadSerializer


@pytest.fixture(scope='function')
def setup_test_environment():
    """Set up the test environment for each test."""
    yield


class TestFileUploadSerializer:
    """Tests for the FileUploadSerializer class."""

    @pytest.fixture(autouse=True)
    def setup(self, setup_test_environment):
        """Set up each test."""
        pass

    def test_valid_file_upload(self):
        """Test serializer with valid file uploads."""
        txt_content = b"This is a test text file"
        csv_content = b"column1,column2\nvalue1,value2"

        txt_file = SimpleUploadedFile("test.txt", txt_content, content_type="text/plain")
        csv_file = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")

        serializer = FileUploadSerializer(data={
            'txt_file': txt_file,
            'csv_file': csv_file
        })

        assert serializer.is_valid() is True
        assert 'txt_file' in serializer.validated_data
        assert 'csv_file' in serializer.validated_data

    def test_missing_files(self):
        """Test serializer validation with missing files."""
        serializer = FileUploadSerializer(data={
            'csv_file': SimpleUploadedFile("test.csv", b"data", content_type="text/csv")
        })
        assert serializer.is_valid() is False
        assert 'txt_file' in serializer.errors

        serializer = FileUploadSerializer(data={
            'txt_file': SimpleUploadedFile("test.txt", b"data", content_type="text/plain")
        })
        assert serializer.is_valid() is False
        assert 'csv_file' in serializer.errors

        serializer = FileUploadSerializer(data={})
        assert serializer.is_valid() is False
        assert 'txt_file' in serializer.errors
        assert 'csv_file' in serializer.errors

    def test_empty_files(self):
        """Test serializer with empty files."""
        txt_file = SimpleUploadedFile("empty.txt", b"test content", content_type="text/plain")
        csv_file = SimpleUploadedFile("empty.csv", b"test,content", content_type="text/csv")

        serializer = FileUploadSerializer(data={
            'txt_file': txt_file,
            'csv_file': csv_file
        })

        assert serializer.is_valid() is True

        empty_txt_file = SimpleUploadedFile("empty.txt", b"", content_type="text/plain")
        empty_csv_file = SimpleUploadedFile("empty.csv", b"", content_type="text/csv")

        serializer = FileUploadSerializer(data={
            'txt_file': empty_txt_file,
            'csv_file': empty_csv_file
        })

        assert serializer.is_valid() is False
        assert 'txt_file' in serializer.errors
        assert 'csv_file' in serializer.errors

    def test_wrong_file_types(self):
        """Test serializer with incorrect file types."""
        pdf_file = SimpleUploadedFile("test.pdf", b"%PDF content", content_type="application/pdf")
        image_file = SimpleUploadedFile("test.jpg", b"image data", content_type="image/jpeg")

        serializer = FileUploadSerializer(data={
            'txt_file': pdf_file,
            'csv_file': image_file
        })

        assert serializer.is_valid() is True

    def test_large_files(self):
        """Test serializer with larger files to ensure no size limitations."""
        large_content = b"x" * (1024 * 1024)
        large_txt_file = SimpleUploadedFile("large.txt", large_content, content_type="text/plain")
        large_csv_file = SimpleUploadedFile("large.csv", large_content, content_type="text/csv")

        serializer = FileUploadSerializer(data={
            'txt_file': large_txt_file,
            'csv_file': large_csv_file
        })

        assert serializer.is_valid() is True
