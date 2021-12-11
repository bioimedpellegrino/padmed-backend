# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import traceback
from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save
from django.dispatch import receiver
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
        
    @classmethod
    def extend_parent(cls,parent_obj):
        try:
            attrs = {}
            for field in parent_obj._meta._get_fields(reverse=False, include_parents=True):
                if field.attname not in attrs:
                    attrs[field.attname] = getattr(parent_obj, field.attname)
            attrs0 = {cls._meta.parents[parent_obj.__class__].name : parent_obj}
            child_obj = cls(**attrs0)
            child_obj.save()
            print(attrs)
            child_obj.__dict__.update(attrs)
            child_obj.save()
            return child_obj
        except Exception as e:
            traceback.print_exc()
            raise(e)
        ## Alternatively
        # child_obj = cls(group_ptr_id=parent_obj.pk)
        # child_obj.__dict__.update(parent_obj.__dict__)
        # child_obj.save()
        # return child_obj
        ## Alternatively
        # for field in parent_obj._meta.fields
        #     setattr(child_obj, field.attname, getattr(parent_obj, field.attname))
        return child_obj
    
    @classmethod
    def get_or_create_from_parent(cls,parent_obj):
        try:
            child_obj = parent_obj.appuser
        except cls.DoesNotExist:
            child_obj = cls.extend_parent(parent_obj)
        return child_obj
        
@receiver(post_save, sender=User)
def create_appuser(sender, instance, created, **kwargs):
    if created:
        AppUser.extend_parent(instance)
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.appuser.save()


class AppGroup(Group):
    """
    This is the base group of this app. It inherit from Group, so all the functionality
    of the Group class can be found here.
    """
    pass

    class Meta():
        verbose_name = _("Application Group")
        verbose_name_plural = _("Application Groups")
        
    @classmethod
    def extend_parent(cls,parent_obj):
        try:
            attrs = {}
            for field in parent_obj._meta._get_fields(reverse=False, include_parents=True):
                if field.attname not in attrs:
                    attrs[field.attname] = getattr(parent_obj, field.attname)
            attrs0 = {cls._meta.parents[parent_obj.__class__].name : parent_obj}
            child_obj = cls(**attrs0)
            child_obj.save()
            print(attrs)
            child_obj.__dict__.update(attrs)
            child_obj.save()
            return child_obj
        except Exception as e:
            traceback.print_exc()
            raise(e)
    
    @classmethod
    def get_or_create_from_parent(cls,parent_obj):
        try:
            child_obj = parent_obj.appgroup
        except cls.DoesNotExist:
            child_obj = cls.extend_parent(parent_obj)
        return child_obj
        
@receiver(post_save, sender=Group)
def create_appgroup(sender, instance, created, **kwargs):
    if created:
        AppGroup.extend_parent(instance)