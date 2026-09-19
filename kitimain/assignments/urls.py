"""assignments/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path('',                                          views.AssignmentListView.as_view()),
    path('<int:pk>/',                                 views.AssignmentDetailView.as_view()),
    path('<int:assignment_id>/submit/',               views.SubmitAssignmentView.as_view()),
    path('<int:assignment_id>/submissions/',          views.AssignmentSubmissionsView.as_view()),
    path('submissions/mine/',                        views.MySubmissionsView.as_view()),
    path('submissions/<int:submission_id>/grade/',   views.GradeSubmissionView.as_view()),
    path('notes/',                                   views.LecturerNoteListView.as_view()),
    path('notes/<int:pk>/',                          views.LecturerNoteDetailView.as_view()),
]
