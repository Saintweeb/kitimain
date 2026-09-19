"""
accounts/models.py
Custom User model for KITI – supports Student and Lecturer roles.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('role', User.ADMIN)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    STUDENT  = 'student'
    LECTURER = 'lecturer'
    ADMIN    = 'admin'
    ROLE_CHOICES = [
        (STUDENT,  'Student'),
        (LECTURER, 'Lecturer'),
        (ADMIN,    'Admin'),
    ]

    email        = models.EmailField(unique=True)
    full_name    = models.CharField(max_length=150)
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    phone        = models.CharField(max_length=20, blank=True)
    avatar       = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    date_joined  = models.DateTimeField(default=timezone.now)
    last_login   = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'User'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.role})'

    @property
    def initials(self):
        parts = self.full_name.split()
        return ''.join(p[0] for p in parts[:2]).upper()


class StudentProfile(models.Model):
    """Extra fields for students."""
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    reg_number  = models.CharField(max_length=30, unique=True)
    course      = models.CharField(max_length=100, default='Diploma ICT')
    year        = models.PositiveSmallIntegerField(default=1)
    enrolled_on = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Student Profile'
        ordering = ['reg_number']

    def __str__(self):
        return f'{self.reg_number} – {self.user.full_name}'


class LecturerProfile(models.Model):
    """Extra fields for lecturers."""
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id    = models.CharField(max_length=30, unique=True)
    department  = models.CharField(max_length=100, default='ICT Department')
    speciality  = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Lecturer Profile'

    def __str__(self):
        return f'{self.staff_id} – {self.user.full_name}'
