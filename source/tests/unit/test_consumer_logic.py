"""
Unit tests for consumer logic in the ProgressConsumer class.

These tests focus on isolated testing of the consumer logic without actually
creating WebSocket connections.
"""
import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import logging

from source.django_layer.api.consumers import ProgressConsumer

pytestmark = pytest.mark.asyncio

logger = logging.getLogger(__name__)


class TestProgressConsumer:
    """Tests for the ProgressConsumer's isolated logic."""

    @pytest.fixture
    def consumer(self):
        """Return a ProgressConsumer instance with mocked socket."""
        consumer = ProgressConsumer()

        consumer.channel_layer = MagicMock()
        consumer.channel_name = "test_channel"
        consumer.scope = {"client": ("127.0.0.1", 8000)}
        consumer.send = AsyncMock()
        consumer.close = AsyncMock()
        consumer.accept = AsyncMock()
        consumer.client_info = "test_client"
        return consumer

    async def test_connect_accepts_connection(self, consumer):
        """Test that connect accepts the WebSocket connection."""
        await consumer.connect()
        consumer.accept.assert_awaited_once()

    async def test_disconnect(self, consumer):
        """Test disconnect doesn't throw errors."""
        await consumer.disconnect(1000)

    @patch('source.django_layer.api.consumers.json.loads')
    async def test_receive_invalid_json(self, mock_loads, consumer):
        """Test handling of invalid JSON in receive."""
        mock_loads.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        await consumer.receive("invalid json")

        consumer.send.assert_awaited_once()
        args, kwargs = consumer.send.call_args
        text_data = args[0] if args else kwargs.get('text_data')
        assert 'error' in text_data
        assert 'Invalid JSON' in text_data

    async def test_receive_unknown_action(self, consumer):
        """Test handling of unknown action in receive."""
        await consumer.receive(json.dumps({"action": "unknown_action"}))

        consumer.send.assert_awaited_once()
        args, kwargs = consumer.send.call_args
        text_data = args[0] if args else kwargs.get('text_data')
        assert 'Unknown action' in json.loads(text_data)['message']

    @patch('source.django_layer.api.consumers.asyncio.create_task')
    async def test_receive_start_processing(self, mock_create_task, consumer):
        """Test handling of 'start_processing' action."""
        message = {
            "action": "start_processing",
            "files": {"txt": "some_file.txt"}
        }

        await consumer.receive(json.dumps(message))

        consumer.send.assert_awaited_once()
        args, kwargs = consumer.send.call_args
        text_data = args[0] if args else kwargs.get('text_data')
        assert 'Backend received' in json.loads(text_data)['message']
        assert 'start_processing' in json.loads(text_data)['message']

        mock_create_task.assert_called_once()
        task_call = mock_create_task.call_args[0][0]
        assert asyncio.iscoroutine(task_call)

    @patch('source.django_layer.api.consumers.Runner')
    @patch('source.django_layer.api.consumers.asyncio.to_thread')
    @patch('source.django_layer.api.consumers.webbrowser.open_new_tab')
    @patch('source.django_layer.api.consumers.Path')
    async def test_run_book_processing_success_flow(self, mock_path, mock_open_tab,
                                                    mock_to_thread, mock_runner, consumer):
        """Test the successful flow of book processing."""
        mock_runner_instance = mock_runner.return_value
        mock_runner_instance.book_name = "The Last Wish"
        mock_runner_instance.book_analyser.get_book_entities.return_value = "entity_df"
        mock_runner_instance.entity_filter.export_filtered_dataframe.return_value = "filtered_df"
        mock_runner_instance.relationship_builder.aggregate_network.return_value = "relationship_df"

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.as_uri.return_value = "file:///path/to/The%20Last%20Wish.html"
        mock_path.return_value = mock_path_instance

        async def mock_to_thread_func(func, *args, **kwargs):
            return func(*args, **kwargs)

        mock_to_thread.side_effect = mock_to_thread_func

        await consumer.run_book_processing("witcher", 1)

        assert consumer.send.await_count >= 6

        mock_open_tab.assert_called_once()
        consumer.close.assert_awaited_once()

    @patch('source.django_layer.api.consumers.Runner')
    @patch('source.django_layer.api.consumers.asyncio.to_thread')
    async def test_run_book_processing_error_handling(self, mock_to_thread, mock_runner, consumer):
        """Test error handling during book processing."""
        mock_runner.side_effect = Exception("Test error")

        await consumer.run_book_processing("witcher", 1)

        send_calls = consumer.send.await_args_list
        error_sent = False
        import json as real_json
        for call in send_calls:
            args = call[0] if len(call) > 0 else ()
            kwargs = call[1] if len(call) > 1 else {}
            if args:
                text_data = args[0]
            else:
                text_data = kwargs.get('text_data')
            if not text_data:
                continue
            try:
                data = real_json.loads(text_data)
            except Exception:
                continue
            if 'error' in data:
                error_sent = True
                assert 'Test error' in data['error'] or data['message']

        assert error_sent, "No error message was sent"
        consumer.close.assert_awaited_once()


# Integration-style tests that use WebsocketCommunicator
@pytest.mark.django_db
class TestProgressConsumerIntegration:
    """Tests for ProgressConsumer using channels test infrastructure."""

    @pytest.fixture(autouse=True)
    def setup_django_settings(self):
        """Configure Django settings for tests."""
        from django.conf import settings

        if not settings.configured:
            settings.configure(
                INSTALLED_APPS=[
                    'channels',
                ],
                CHANNEL_LAYERS={
                    "default": {
                        "BACKEND": "channels.layers.InMemoryChannelLayer",
                    },
                },
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                ASGI_APPLICATION='source.django_layer.api.routing.application',
            )
        yield
