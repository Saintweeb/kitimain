"""attendance/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.AttendanceListView.as_view()),
    path('mine/',                          views.MyAttendanceView.as_view()),
    path('bulk-mark/',                     views.BulkMarkAttendanceView.as_view()),
    path('summary/',                       views.AttendanceSummaryView.as_view()),
    path('summary/<int:student_id>/',      views.StudentAttendanceSummaryView.as_view()),
]
