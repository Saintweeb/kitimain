from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display  = ['original_name', 'category', 'uploaded_by', 'file_size_kb', 'created_at']
    list_filter   = ['category']
    search_fields = ['original_name', 'uploaded_by__full_name']
