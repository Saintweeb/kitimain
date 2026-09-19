"""
collaboration/consumers.py  –  Django Channels WebSocket consumer.
Real-time chat for each Room.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id    = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'room_{self.room_id}'

        # Join channel group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Notify others that a user joined
        user = self.scope.get('user')
        if user and user.is_authenticated:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type':   'system_message',
                    'text':   f'{user.full_name} joined the room.',
                    'sender': '__system__',
                }
            )

    async def disconnect(self, close_code):
        user = self.scope.get('user')
        if user and user.is_authenticated:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type':   'system_message',
                    'text':   f'{user.full_name} left the room.',
                    'sender': '__system__',
                }
            )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope.get('user')

        if not user or not user.is_authenticated:
            return

        msg_type = data.get('type', 'chat')

        if msg_type == 'chat':
            text = data.get('text', '').strip()
            if not text:
                return

            # Persist to DB
            await self.save_message(user, text)

            # Broadcast
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type':     'chat_message',
                    'text':     text,
                    'sender':   user.full_name,
                    'initials': user.initials,
                    'user_id':  user.id,
                    'time':     timezone.now().strftime('%H:%M'),
                }
            )

        elif msg_type == 'code_update':
            # Broadcast live code changes (not persisted – just sync)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type':     'code_update',
                    'code':     data.get('code', ''),
                    'language': data.get('language', 'python'),
                    'sender':   user.full_name,
                    'user_id':  user.id,
                }
            )

    # ── Handlers ──────────────────────────────────────────
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type':     'chat',
            'text':     event['text'],
            'sender':   event['sender'],
            'initials': event['initials'],
            'user_id':  event['user_id'],
            'time':     event['time'],
        }))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            'type':   'system',
            'text':   event['text'],
        }))

    async def code_update(self, event):
        await self.send(text_data=json.dumps({
            'type':     'code_update',
            'code':     event['code'],
            'language': event['language'],
            'sender':   event['sender'],
            'user_id':  event['user_id'],
        }))

    # ── DB helpers ────────────────────────────────────────
    @database_sync_to_async
    def save_message(self, user, text):
        from .models import Message, Room
        try:
            room = Room.objects.get(pk=self.room_id)
            Message.objects.create(room=room, sender=user, text=text)
        except Room.DoesNotExist:
            pass
