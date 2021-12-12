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
    pass

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass