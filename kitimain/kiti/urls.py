"""
KITI ICT Department – Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import CustomTokenObtainPairView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/login/',            CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/',          TokenRefreshView.as_view(),          name='token_refresh'),
    path('api/auth/logout/',           LogoutView.as_view(),                name='logout'),

    # Password reset
    path('api/auth/',                  include('accounts.password_reset_urls')),

    # Apps
    path('api/accounts/',      include('accounts.urls')),
    path('api/courses/',       include('courses.urls')),
    path('api/assignments/',   include('assignments.urls')),
    path('api/assessments/',   include('assessments.urls')),
    path('api/attendance/',    include('attendance.urls')),
    path('api/collaboration/', include('collaboration.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/',       include('reports.urls')),
    path('api/uploads/',       include('uploads.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header  = 'KITI ICT Department'
admin.site.site_title   = 'KITI Admin'
admin.site.index_title  = 'Administration Panel'
