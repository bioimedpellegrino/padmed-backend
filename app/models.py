# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import traceback
from django.db import models
from django.contrib.auth.models import User,Group
from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class AppUser(User):
    """e
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
    def extend_parent(cls,parent_obj:User):
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
    def get_or_create_from_parent(cls,parent_obj:User):
        try:
            child_obj = parent_obj.appuser
        except cls.DoesNotExist:
            child_obj = cls.extend_parent(parent_obj)
        return child_obj
    
    def viewable_hospitals(self)->list():
        """Returns a list of all the hospital with respect to wich the user has viewer permissions"""
        try:
            groups = self.groups.filter()
            
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(type(self))
            all_permissions = Permission.objects.filter(content_type=content_type)
            for permission in all_permissions:
                print(permission.codename,permission.name,permission)
            
            return
        except Exception as e:
            traceback.print_exc()
            raise(e)
    
@receiver(post_save, sender=User)
def create_appuser(sender, instance, created, **kwargs):
    if created:
        AppUser.extend_parent(instance)

class AppGroup(Group):
    """
    This is the base group of this app. It inherit from Group, so all the functionality
    of the Group class can be found here.
    """
    ## See 
    # https://docs.djangoproject.com/en/3.2/ref/contrib/contenttypes/ at 
    # https://docs.djangoproject.com/en/3.2/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey
    # for generic relations and their utility
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta():
        verbose_name = _("Application Group")
        verbose_name_plural = _("Application Groups")
        
    @classmethod
    def extend_parent(cls,parent_obj:Group):
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
    def get_or_create_from_parent(cls,parent_obj:Group):
        try:
            child_obj = parent_obj.appgroup
        except cls.DoesNotExist:
            child_obj = cls.extend_parent(parent_obj)
        return child_obj
        
@receiver(post_save, sender=Group)
def create_appgroup(sender, instance, created, **kwargs):
    if created:
        AppGroup.extend_parent(instance)
        

class RestrictedClass(models.Model):
    
    ## See 
    # https://docs.djangoproject.com/en/3.2/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey
    # for generic relations and their utility
    # and https://docs.djangoproject.com/en/3.2/topics/db/models/ for generic related_name values in abstract classes
    
    name = models.CharField(blank=True, null=True, max_length=512, default="")
    ## Permission Groups ##
    groups = GenericRelation(AppGroup,related_name="%(app_label)s_%(class)s_set", related_query_name='%(app_label)s_%(class)s')
    
    class Meta():
        abstract = True
        
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        models.signals.post_save.connect(create_groups, sender=cls)
        
    def get_or_create_groups(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        try:
            content_type = ContentType.objects.get_for_model(type(self))
            
            ## Look for lacking groups
            existing_group_tags = self.groups.values_list("tag",flat=True)
            
            admins_tag = "%s_%s_%s_admins"%(content_type.app_label.lower(),content_type.model.lower(),self.id)
            creators_tag = "%s_%s_%s_creators"%(content_type.app_label.lower(),content_type.model.lower(),self.id)
            editors_tag = "%s_%s_%s_editors"%(content_type.app_label.lower(),content_type.model.lower(),self.id)
            viewers_tag = "%s_%s_%s_viewers"%(content_type.app_label.lower(),content_type.model.lower(),self.id)
            
            group_tags_to_create = set([admins_tag,creators_tag,editors_tag,viewers_tag]).difference(set(existing_group_tags))
            if group_tags_to_create:
                ## Create Groups
                all_permissions = Permission.objects.filter(content_type=content_type)
                view_perm = all_permissions.get(codename__startswith="view").id
                add_perm = all_permissions.get(codename__startswith="add").id
                change_perm = all_permissions.get(codename__startswith="change").id
                delete_perm = all_permissions.get(codename__startswith="delete").id
                all_groups_params ={
                    admins_tag:{
                        "name":"%s - %s (id: %s) - Admins"%(content_type.model.capitalize(),self.name,self.id),
                        "permissions":[view_perm,add_perm,change_perm,delete_perm],
                    },
                    creators_tag:{
                        "name":"%s - %s (id: %s) - Creators"%(content_type.model.capitalize(),self.name,self.id),
                        "permissions":[view_perm,add_perm,change_perm,delete_perm],
                    },
                    editors_tag:{
                        "name":"%s - %s (id: %s) - Editors"%(content_type.model.capitalize(),self.name,self.id),
                        "permissions":[view_perm,change_perm],
                            
                    },
                    viewers_tag:{
                        "name":"%s - %s (id: %s) - Viewers"%(content_type.model.capitalize(),self.name,self.id),
                        "permissions":[view_perm],
                    },
                }
                for group_tag_to_create in group_tags_to_create:
                    app_group = AppGroup(
                        tag = group_tag_to_create,
                        name = all_groups_params[group_tag_to_create]["name"],
                        content_object=self
                        )
                    app_group.save()
                    app_group.permissions.add(*all_groups_params[group_tag_to_create]["permissions"])
                    
            groups = self.groups.all()
            return groups
        except Exception as e:
            traceback.print_exc()
            raise(e)

def create_groups(sender, instance, created, **kwargs):
    if created:
        instance.get_or_create_groups()