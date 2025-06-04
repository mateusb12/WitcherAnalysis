"""
Unit tests for consumer logic in the ProgressConsumer class.

These tests focus on isolated testing of the consumer logic without actually
creating WebSocket connections.
"""
import json
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from channels.testing import WebsocketCommunicator
from django.test import override_settings

# Import the consumer to test
from source.django_layer.api.consumers import ProgressConsumer

pytestmark = pytest.mark.asyncio  # Mark all tests as asyncio tests


class TestProgressConsumer:
    """Tests for the ProgressConsumer's isolated logic."""

    @pytest.fixture
    async def consumer(self):
        """Return a ProgressConsumer instance with mocked socket."""
        consumer = ProgressConsumer()
        # Mock the channel layer and other attributes
        consumer.channel_layer = MagicMock()
        consumer.channel_name = "test_channel"
        consumer.scope = {"client": ("127.0.0.1", 8000)}
        consumer.send = AsyncMock()
        consumer.close = AsyncMock()
        return consumer

    async def test_connect_accepts_connection(self, consumer):
        """Test that connect accepts the WebSocket connection."""
        await consumer.connect()
        consumer.accept.assert_awaited_once()

    async def test_disconnect(self, consumer):
        """Test disconnect doesn't throw errors."""
        await consumer.disconnect(1000)  # Normal closure code
        # No exceptions should be raised

    @patch('source.django_layer.api.consumers.json.loads')
    async def test_receive_invalid_json(self, mock_loads, consumer):
        """Test handling of invalid JSON in receive."""
        mock_loads.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        await consumer.receive("invalid json")

        # Check that an error message was sent
        consumer.send.assert_awaited_once()
        args, kwargs = consumer.send.call_args
        text_data = args[1] if args else kwargs.get('text_data')
        assert 'error' in json.loads(text_data)
        assert 'Invalid JSON' in json.loads(text_data)['error']

    async def test_receive_unknown_action(self, consumer):
        """Test handling of unknown action in receive."""
        await consumer.receive(json.dumps({"action": "unknown_action"}))

        # Check that an appropriate message was sent
        consumer.send.assert_awaited_once()
        args, kwargs = consumer.send.call_args
        text_data = args[0] if args else kwargs.get('text_data')
        assert 'Unknown action' in json.loads(text_data)['message']

    @patch('source.django_layer.api.consumers.asyncio.create_task')
    async def test_receive_start_processing(self, mock_create_task, consumer):
        """Test handling of 'start_processing' action."""
        # Prepare the message
        message = {
            "action": "start_processing",
            "files": {"txt": "some_file.txt"}
        }

        # Call the method
        await consumer.receive(json.dumps(message))

        # Check that a message was sent confirming receipt
        consumer.send.assert_awaited_once()
        args, kwargs = consumer.send.call_args
        text_data = args[0] if args else kwargs.get('text_data')
        assert 'Backend received' in json.loads(text_data)['message']
        assert 'start_processing' in json.loads(text_data)['message']

        # Verify that a task was created for processing
        mock_create_task.assert_called_once()
        task_call = mock_create_task.call_args[0][0]
        assert asyncio.iscoroutine(task_call)  # Make sure it's a coroutine

    @patch('source.django_layer.api.consumers.Runner')
    @patch('source.django_layer.api.consumers.asyncio.to_thread')
    @patch('source.django_layer.api.consumers.webbrowser.open_new_tab')
    @patch('source.django_layer.api.consumers.Path')
    async def test_run_book_processing_success_flow(self, mock_path, mock_open_tab,
                                               mock_to_thread, mock_runner, consumer):
        """Test the successful flow of book processing."""
        # Set up all the mocks
        mock_runner_instance = mock_runner.return_value
        mock_runner_instance.book_name = "The Last Wish"
        mock_runner_instance.book_analyser.get_book_entities.return_value = "entity_df"
        mock_runner_instance.entity_filter.export_filtered_dataframe.return_value = "filtered_df"
        mock_runner_instance.relationship_builder.aggregate_network.return_value = "relationship_df"

        # Mock Path for HTML file check
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.as_uri.return_value = "file:///path/to/The%20Last%20Wish.html"
        mock_path.return_value = mock_path_instance

        # Mock asyncio.to_thread to directly return values instead of awaiting
        async def mock_to_thread_func(func, *args, **kwargs):
            return func(*args, **kwargs)

        mock_to_thread.side_effect = mock_to_thread_func

        # Call the method
        await consumer.run_book_processing("witcher", 1)

        # Verify the process was completed and all messages were sent
        assert consumer.send.await_count >= 6  # At least 6 progress messages

        # Check for completion and browser opening
        mock_open_tab.assert_called_once()
        consumer.close.assert_awaited_once()

    @patch('source.django_layer.api.consumers.Runner')
    @patch('source.django_layer.api.consumers.asyncio.to_thread')
    async def test_run_book_processing_error_handling(self, mock_to_thread, mock_runner, consumer):
        """Test error handling during book processing."""
        # Make the Runner throw an exception
        mock_runner.side_effect = Exception("Test error")

        # Call the method
        await consumer.run_book_processing("witcher", 1)

        # Verify error message was sent and connection closed
        send_calls = consumer.send.await_args_list
        error_sent = False
        for call in send_calls:
            args = call[0]
            data = json.loads(args[0])
            if 'error' in data:
                error_sent = True
                assert 'Test error' in data['error'] or data['message']

        assert error_sent, "No error message was sent"
        consumer.close.assert_awaited_once()


# Integration-style tests that use WebsocketCommunicator
@pytest.mark.django_db
class TestProgressConsumerIntegration:
    """Tests for ProgressConsumer using channels test infrastructure."""

    @pytest.fixture
    def communicator(self):
        """Create a WebsocketCommunicator for testing."""
        from django.conf import settings
        from channels.routing import URLRouter
        from django.urls import re_path

        # Create a custom application with just our consumer
        application = URLRouter([
            re_path(r"^ws/progress/$", ProgressConsumer.as_asgi()),
        ])

        # Return a communicator connected to the application
        return WebsocketCommunicator(application, "/ws/progress/")

    @patch('source.django_layer.api.consumers.asyncio.create_task')
    async def test_consumer_connection_flow(self, mock_create_task, communicator):
        """Test the consumer's WebSocket connection flow."""
        connected, _ = await communicator.connect()
        assert connected, "Could not connect to WebSocket"

        # Send a message
        await communicator.send_json_to({
            "action": "start_processing",
            "files": {"txt": "test_book.txt"}
        })

        # Get response
        response = await communicator.receive_json_from()
        assert "message" in response
        assert "start_processing" in response["message"]

        # Verify task creation
        mock_create_task.assert_called_once()

        # Close the connection
        await communicator.disconnect()
