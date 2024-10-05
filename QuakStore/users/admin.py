from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from cart.models import CartItem
from django.utils.translation import gettext_lazy as _
# Register your models here.


class ProductsInline(admin.TabularInline):
    model= CartItem
    extra= 1

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    inlines = [ProductsInline]