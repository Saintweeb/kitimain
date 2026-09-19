from django.urls import path
from . import views
urlpatterns = [
    path('student/<int:student_id>/', views.StudentProgressReportView.as_view()),
    path('class/',                    views.ClassReportView.as_view()),
]
