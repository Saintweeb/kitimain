"""uploads/views.py"""
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from django.conf import settings
from .models import UploadedFile
from .serializers import UploadedFileSerializer


ALLOWED_EXTENSIONS = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', [
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.ppt', '.pptx', '.txt', '.zip',
    '.png', '.jpg', '.jpeg', '.gif',
    '.mp4', '.py', '.html', '.css', '.js',
])

MAX_FILE_SIZE = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)


class FileUploadView(APIView):
    """
    POST /api/uploads/
    Multipart form: file=<file>, category=<category>
    Returns: { id, file_url, original_name, ... }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': 'No file provided.'}, status=400)

        # Validate extension
        _, ext = os.path.splitext(uploaded.name)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            return Response({
                'detail': f'File type "{ext}" not allowed.',
                'allowed': ALLOWED_EXTENSIONS,
            }, status=400)

        # Validate size
        if uploaded.size > MAX_FILE_SIZE:
            return Response({
                'detail': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB.',
            }, status=400)

        category = request.data.get('category', UploadedFile.CATEGORY_OTHER)

        record = UploadedFile.objects.create(
            file=uploaded,
            original_name=uploaded.name,
            category=category,
            file_size=uploaded.size,
            mime_type=uploaded.content_type or '',
            uploaded_by=request.user,
        )

        serializer = UploadedFileSerializer(record, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyFilesView(generics.ListAPIView):
    """GET /api/uploads/mine/  – list my uploaded files"""
    serializer_class   = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields   = ['category']

    def get_queryset(self):
        return UploadedFile.objects.filter(uploaded_by=self.request.user)


class FileDeleteView(APIView):
    """DELETE /api/uploads/<id>/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            f = UploadedFile.objects.get(pk=pk, uploaded_by=request.user)
        except UploadedFile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        f.delete()
        return Response({'detail': 'File deleted.'}, status=204)
