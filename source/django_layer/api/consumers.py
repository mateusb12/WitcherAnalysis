import asyncio
import json
import logging  # Added
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)  # Added


class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"WebSocket connect: client={self.scope.get('client')}")
        await self.accept()
        logger.info(f"WebSocket accepted: client={self.scope.get('client')}")

        try:
            logger.info(f"Starting progress loop for: client={self.scope.get('client')}")
            # This loop sends 1001 messages for 0.0% to 100.0%
            for i in range(1001):
                message = {'increment': 0.1}

                if i % 200 == 0 or i == 1000:  # Log every 20% or at the last increment
                    logger.info(f"Sending increment {i + 1}/1001 (value: 0.1) for client={self.scope.get('client')}")

                await self.send(text_data=json.dumps(message))
                await asyncio.sleep(0.05)  # 50ms delay; total ~50 seconds

            logger.info(f"Finished progress loop for: client={self.scope.get('client')}")
            await self.send(text_data=json.dumps({'progress': 100}))
            logger.info(f"Sent final progress 100 for: client={self.scope.get('client')}")

        except Exception as e:
            logger.error(f"Error in progress loop for client={self.scope.get('client')}: {e}", exc_info=True)
        finally:
            logger.info(f"Closing WebSocket connection from server side for: client={self.scope.get('client')}")
            await self.close()

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnect: client={self.scope.get('client')}, code={close_code}")
        pass

    async def receive(self, text_data):
        logger.info(f"WebSocket receive from client={self.scope.get('client')}: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')

            if action == 'start_processing':
                files = text_data_json.get('files', {})
                logger.info(f"Received 'start_processing' action. Files: {files}. Client: {self.scope.get('client')}")
                await self.send(text_data=json.dumps({
                    'message': f"Processing started by backend for files: TXT-{files.get('txt', 'N/A')}, CSV-{files.get('csv', 'N/A')}"
                }))
            else:
                logger.warning(
                    f"Received unknown action or non-JSON message: {text_data} from client={self.scope.get('client')}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from client={self.scope.get('client')}: {text_data}", exc_info=True)
        except Exception as e:
            logger.error(f"Error in receive method for client={self.scope.get('client')}: {e}", exc_info=True)
