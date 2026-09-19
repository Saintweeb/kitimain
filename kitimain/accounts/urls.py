from django.urls import path
from . import views

urlpatterns = [
    path('me/',                    views.MeView.as_view(),           name='me'),
    path('change-password/',       views.ChangePasswordView.as_view(), name='change-password'),
    path('register/',              views.RegisterView.as_view(),     name='register'),
    path('students/',              views.StudentListView.as_view(),   name='student-list'),
    path('students/<int:pk>/',     views.StudentDetailView.as_view(), name='student-detail'),
    path('students/<int:pk>/stats/', views.StudentStatsView.as_view(), name='student-stats'),
]
