from django.urls import path
from . import views
urlpatterns = [
    path('',          views.FileUploadView.as_view()),
    path('mine/',     views.MyFilesView.as_view()),
    path('<int:pk>/', views.FileDeleteView.as_view()),
]
