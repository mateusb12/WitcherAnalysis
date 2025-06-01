import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Start sending progress updates
        for i in range(101):
            await self.send(text_data=json.dumps({
                'progress': i
            }))
            await asyncio.sleep(0.1) # Simulate work being done
        await self.close()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # You can handle messages from the client here if needed
        pass
