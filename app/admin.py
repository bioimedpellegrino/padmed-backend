# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import *

class AppUserAdmin(admin.ModelAdmin):
    pass

admin.site.register(AppUser, AppUserAdmin)
