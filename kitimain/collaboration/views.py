"""collaboration/views.py"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Room, Message, CodeSnapshot
from .serializers import RoomSerializer, MessageSerializer, CodeSnapshotSerializer
from accounts.permissions import IsLecturerOrAdmin


class RoomListView(generics.ListCreateAPIView):
    serializer_class   = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields   = ['type']
    search_fields      = ['name']

    def get_queryset(self):
        user = self.request.user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Lecturers see all; students see only rooms they belong to
        if user.role in (User.LECTURER, User.ADMIN):
            return Room.objects.filter(is_active=True).prefetch_related('members')
        return user.rooms.filter(is_active=True).prefetch_related('members')

    def perform_create(self, serializer):
        room = serializer.save(created_by=self.request.user)
        room.members.add(self.request.user)


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = Room.objects.prefetch_related('members')
    serializer_class   = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]


class JoinRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id, is_active=True)
        room.members.add(request.user)
        return Response({'detail': f'Joined {room.name}'})

    def delete(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        room.members.remove(request.user)
        return Response({'detail': f'Left {room.name}'})


class MessageListView(generics.ListCreateAPIView):
    serializer_class   = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            room_id=self.kwargs['room_id']
        ).select_related('sender').order_by('created_at')

    def perform_create(self, serializer):
        room = get_object_or_404(Room, pk=self.kwargs['room_id'])
        serializer.save(sender=self.request.user, room=room)


class CodeSnapshotListView(generics.ListCreateAPIView):
    serializer_class   = CodeSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CodeSnapshot.objects.filter(
            room_id=self.kwargs['room_id']
        ).select_related('saved_by')

    def perform_create(self, serializer):
        room = get_object_or_404(Room, pk=self.kwargs['room_id'])
        serializer.save(saved_by=self.request.user, room=room)


class CodeSnapshotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = CodeSnapshot.objects.all()
    serializer_class   = CodeSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]
