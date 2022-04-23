# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import Permission
from .models import *
from django.utils.translation import gettext_lazy as _

@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('User parameters'), {'fields': ('_dashboard_hospital', 'use_card_reader')}),
        (_('Visualization'), {'fields': ('theme', '_dashboard_options')}),
        (_('User type'), {'fields': ('totem_logged', 'patient_logged')}),
    )

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass