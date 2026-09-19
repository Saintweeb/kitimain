"""collaboration/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path('rooms/',                                  views.RoomListView.as_view()),
    path('rooms/<int:pk>/',                         views.RoomDetailView.as_view()),
    path('rooms/<int:room_id>/join/',               views.JoinRoomView.as_view()),
    path('rooms/<int:room_id>/messages/',           views.MessageListView.as_view()),
    path('rooms/<int:room_id>/snapshots/',          views.CodeSnapshotListView.as_view()),
    path('snapshots/<int:pk>/',                     views.CodeSnapshotDetailView.as_view()),
]
