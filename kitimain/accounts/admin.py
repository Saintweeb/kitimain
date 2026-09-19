from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, LecturerProfile


class StudentInline(admin.StackedInline):
    model  = StudentProfile
    extra  = 0
    fields = ['reg_number', 'course', 'year']


class LecturerInline(admin.StackedInline):
    model  = LecturerProfile
    extra  = 0
    fields = ['staff_id', 'department', 'speciality']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display   = ['full_name', 'email', 'role', 'is_active', 'date_joined']
    list_filter    = ['role', 'is_active', 'is_staff']
    search_fields  = ['full_name', 'email']
    ordering       = ['full_name']
    inlines        = [StudentInline, LecturerInline]
    fieldsets = (
        (None,            {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone', 'avatar')}),
        ('Role',          {'fields': ('role',)}),
        ('Permissions',   {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates',         {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ['reg_number', 'user', 'course', 'year', 'enrolled_on']
    list_filter   = ['year', 'course']
    search_fields = ['reg_number', 'user__full_name']


@admin.register(LecturerProfile)
class LecturerProfileAdmin(admin.ModelAdmin):
    list_display  = ['staff_id', 'user', 'department', 'speciality']
    search_fields = ['staff_id', 'user__full_name']
