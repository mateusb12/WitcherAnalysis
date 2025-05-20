from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WebSocket connect called")
        session = self.scope.get("session")
        if not session or not session.session_key:
            print("No session or session key found!")
            await self.close()
            return

        self.group_name = f'progress_{self.scope["session"].session_key}'

        # Join a group based on the session key (or any identifier)
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        print(f"Added to group: {self.group_name}")
        await self.accept()

    async def disconnect(self, close_code):
        print("WebSocket disconnect called")
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Handler to receive messages from the group.
    async def progress_update(self, event):
        progress = event['progress']
        print(f"Sending progress update: {progress}")
        # Send the progress update to WebSocket client
        await self.send(text_data=json.dumps({'progress': progress}))
