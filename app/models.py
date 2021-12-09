# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class AppUser(User):
    """
    This is the base user of this app. It inherit from User, so all the functionality
    of the User class can be found here.
    """
    light_theme = "light"
    darl_theme = "dark"
    THEMES = (
        (light_theme,_("Chiaro")),
        (darl_theme,_("Scuro"))
    )
    theme = models.CharField(verbose_name=_("Tema"),max_length=512, choices=THEMES,default="light")
    _dashboard_options = models.TextField(verbose_name=_("Opzioni Dashboard"),default="{}")

    class Meta():
        verbose_name = _("Application User")
        verbose_name_plural = _("Application Users")
        
    @property
    def dashboard_options(self):
        from app.utils import AttributeJson
        return AttributeJson(self,"_dashboard_options")
    @dashboard_options.setter
    def dashboard_options(self,value):
        import json
        self._dashboard_options = json.dumps(value)
