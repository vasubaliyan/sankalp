# Dashboard/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("dashboard_updates", self.channel_name)
        await self.accept()
        print("✅ WebSocket connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard_updates", self.channel_name)
        print("❌ WebSocket disconnected")

    async def receive(self, text_data):
        # optional (if frontend sends messages)
        pass

    async def send_dashboard_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "update",
            "message": event["message"],
        }))
