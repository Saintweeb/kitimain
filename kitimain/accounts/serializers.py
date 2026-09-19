"""
accounts/serializers.py
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import StudentProfile, LecturerProfile

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend JWT payload with user role and name."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['full_name'] = user.full_name
        token['role']      = user.role
        token['email']     = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id':        self.user.id,
            'email':     self.user.email,
            'full_name': self.user.full_name,
            'role':      self.user.role,
            'initials':  self.user.initials,
        }
        return data


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = StudentProfile
        fields = ['reg_number', 'course', 'year', 'enrolled_on']


class LecturerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LecturerProfile
        fields = ['staff_id', 'department', 'speciality']


class UserSerializer(serializers.ModelSerializer):
    student_profile  = StudentProfileSerializer(read_only=True)
    lecturer_profile = LecturerProfileSerializer(read_only=True)
    avatar_url       = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id', 'email', 'full_name', 'role', 'phone',
            'avatar_url', 'date_joined', 'last_login',
            'student_profile', 'lecturer_profile',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class RegisterSerializer(serializers.ModelSerializer):
    """Used by admin/lecturer to create student accounts."""
    password        = serializers.CharField(write_only=True, min_length=8)
    reg_number      = serializers.CharField(required=False)
    course          = serializers.CharField(required=False, default='Diploma ICT')
    year            = serializers.IntegerField(required=False, default=1)
    staff_id        = serializers.CharField(required=False)
    department      = serializers.CharField(required=False, default='ICT Department')

    class Meta:
        model  = User
        fields = [
            'email', 'full_name', 'role', 'phone', 'password',
            'reg_number', 'course', 'year', 'staff_id', 'department',
        ]

    def create(self, validated_data):
        role       = validated_data.get('role', User.STUDENT)
        reg_number = validated_data.pop('reg_number', None)
        course     = validated_data.pop('course', 'Diploma ICT')
        year       = validated_data.pop('year', 1)
        staff_id   = validated_data.pop('staff_id', None)
        department = validated_data.pop('department', 'ICT Department')
        password   = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if role == User.STUDENT:
            StudentProfile.objects.create(
                user=user,
                reg_number=reg_number or f'D{user.id:04d}/ICT/{__import__("datetime").date.today().year}',
                course=course,
                year=year,
            )
        elif role == User.LECTURER:
            LecturerProfile.objects.create(
                user=user,
                staff_id=staff_id or f'KITI-L{user.id:04d}',
                department=department,
            )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
