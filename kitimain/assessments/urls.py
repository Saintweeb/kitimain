"""assessments/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.CATListView.as_view()),
    path('<int:pk>/',                     views.CATDetailView.as_view()),
    path('<int:cat_id>/questions/',       views.QuestionCreateView.as_view()),
    path('questions/<int:pk>/',          views.QuestionDetailView.as_view()),
    path('<int:cat_id>/start/',           views.StartCATView.as_view()),
    path('<int:cat_id>/submit/',          views.SubmitCATView.as_view()),
    path('<int:cat_id>/attempts/',        views.CATAttemptsView.as_view()),
    path('<int:cat_id>/status/',          views.ToggleCATStatusView.as_view()),
    path('my-attempts/',                  views.MyCATAttemptsView.as_view()),
]
