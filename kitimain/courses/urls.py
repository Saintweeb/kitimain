"""courses/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path('modules/',                         views.ModuleListView.as_view()),
    path('modules/<int:pk>/',                views.ModuleDetailView.as_view()),
    path('modules/<int:module_id>/progress/',views.ModuleProgressView.as_view()),
    path('my-progress/',                     views.MyModuleProgressListView.as_view()),
    path('classes/',                         views.OnlineClassListView.as_view()),
    path('classes/<int:pk>/',                views.OnlineClassDetailView.as_view()),
    path('announcements/',                   views.AnnouncementListView.as_view()),
    path('announcements/<int:pk>/',          views.AnnouncementDetailView.as_view()),
    path('revision-papers/',                 views.RevisionPaperListView.as_view()),
    path('revision-papers/<int:pk>/',        views.RevisionPaperDetailView.as_view()),
]
