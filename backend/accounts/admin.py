from django.contrib import admin

from .models import AuthUser, Customerprofile, Userprofile


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("date_joined", "last_login", "password")


@admin.register(Userprofile)
class UserprofileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_vendor", "created_at", "updated_at")
    list_filter = ("is_vendor",)


@admin.register(Customerprofile)
class CustomerprofileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at", "updated_at")
