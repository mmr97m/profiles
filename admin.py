from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmployeeSalary, User, ManagerProfile, EmployeeCategory, EmployeeProfile, SubManagerProfile, CustomerProfile, WorkDay

@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone', 'email', 'gender', 'avatar')
            }),
        (('Permissions'), {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
            }),
        (('Important dates'), {'fields': ('birthdate', 'last_login', 'date_joined')}),
    )

@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user','speciality',)
    ordering = ('user',)
    search_fields = ('user', 'speciality',)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user','category',)
    ordering = ('user',)
    search_fields = ('user', 'category',)

@admin.register(EmployeeCategory)
class EmployeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','slug',)
    ordering = ('name',)
    search_fields = ('name', 'slug',)


@admin.register(SubManagerProfile)
class SubManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    ordering = ('user',)
    search_fields = ('user',)


admin.site.register(WorkDay)
admin.site.register(CustomerProfile)
admin.site.register(EmployeeSalary)
