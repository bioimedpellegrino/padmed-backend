# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin,GroupAdmin
from .models import *

@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    pass

@admin.register(AppGroup)
class AppGroupAdmin(GroupAdmin):
    pass