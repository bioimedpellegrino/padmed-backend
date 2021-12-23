# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import traceback,os
from django.db import models
from django.contrib.auth.models import User,Group
from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class RestrictedClass(models.Model):
    TYPES = ["view","add","change","delete","admin"]
    
    class Meta():
        abstract = True
        
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        models.signals.post_save.connect(auto_create_permissions, sender=cls)
        models.signals.post_delete.connect(auto_delete_permissions,sender=cls)
        
    def create_permissions(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Group
        try:
            content_type = ContentType.objects.get_for_model(self)
            
            ## Get or create permissions
            class_permissions = {}
            instance_permissions = {}
            for type in self.TYPES:
                class_permissions[type],c = Permission.objects.get_or_create(
                    content_type=content_type,
                    codename = get_class_permission_codename(type,self),
                    defaults={
                        "name": get_class_permission_name(type,self)
                    }
                )
                instance_permissions[type],c = Permission.objects.get_or_create(
                    content_type=content_type,
                    codename = get_instance_permission_codename(type,self),
                    defaults={
                        "name": get_instance_permission_name(type,self)
                    }
                )
            
            ## DEFINE INSTANCE PERMISSION GROUPS
            
            view_perm = instance_permissions["view"]
            add_perm = instance_permissions["add"] 
            change_perm = instance_permissions["change"] 
            delete_perm = instance_permissions["delete"] 
            admin_perm = instance_permissions["admin"] 
            
            ## Get group names
            admins_name = AppGroup.get_admins_name(content_type,self)
            creators_name = AppGroup.get_creators_name(content_type,self)
            editors_name = AppGroup.get_editors_name(content_type,self)
            viewers_name = AppGroup.get_viewers_name(content_type,self)
            ## Define per-group permissions
            all_groups_params ={
                admins_name:{
                    "permissions":[view_perm,change_perm,add_perm,delete_perm,admin_perm],
                },
                creators_name:{
                    "permissions":[view_perm,change_perm,add_perm,delete_perm],
                },
                editors_name:{
                    "permissions":[view_perm,change_perm],
                        
                },
                viewers_name:{
                    "permissions":[view_perm],
                },
            }
            for group_name_to_create in all_groups_params:
                app_group,c = Group.objects.get_or_create(
                    name = group_name_to_create,
                    )
                app_group.save()
                app_group.permissions.set(all_groups_params[group_name_to_create]["permissions"])
            
            ## DEFINE CLASS PERMISSION GROUPS
            
            view_perm = class_permissions["view"]
            add_perm = class_permissions["add"] 
            change_perm = class_permissions["change"] 
            delete_perm = class_permissions["delete"] 
            admin_perm = class_permissions["admin"] 
            
            ## Get group names
            admins_name = AppGroup.get_admins_name(content_type)
            creators_name = AppGroup.get_creators_name(content_type)
            editors_name = AppGroup.get_editors_name(content_type)
            viewers_name = AppGroup.get_viewers_name(content_type)
            ## Define per-group permissions
            all_groups_params ={
                admins_name:{
                    "permissions":[view_perm,change_perm,add_perm,delete_perm,admin_perm],
                },
                creators_name:{
                    "permissions":[view_perm,change_perm,add_perm,delete_perm],
                },
                editors_name:{
                    "permissions":[view_perm,change_perm],
                        
                },
                viewers_name:{
                    "permissions":[view_perm],
                },
            }
            for group_name_to_create in all_groups_params:
                app_group,c = Group.objects.get_or_create(
                    name = group_name_to_create,
                    )
                app_group.save()
                app_group.permissions.set(all_groups_params[group_name_to_create]["permissions"])
                    
        except Exception as e:
            traceback.print_exc()
            raise(e)
        
    def delete_permissions(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Group
        try:
            content_type = ContentType.objects.get_for_model(self)
            
            ## Get or create permissions
            
            instance_permissions = {}
            for type in self.TYPES:
                Permission.objects.filter(
                    content_type=content_type,
                    codename = get_class_permission_codename(type,self),
                ).delete()
                instance_permissions[type] = Permission.objects.filter(
                    content_type=content_type,
                    codename = get_instance_permission_codename(type,self)
                ).delete()
            
            ## Get group names
            admins_name = AppGroup.get_admins_name(content_type,self)
            creators_name = AppGroup.get_creators_name(content_type,self)
            editors_name = AppGroup.get_editors_name(content_type,self)
            viewers_name = AppGroup.get_viewers_name(content_type,self)
            ## Define per-group permissions
            all_groups_params ={
                admins_name,
                creators_name,
                editors_name,
                viewers_name,
            }
            for group_name_to_create in all_groups_params:
                app_group = Group.objects.filter(
                    name = group_name_to_create,
                    ).delete()
                    
        except Exception as e:
            traceback.print_exc()
            raise(e)

    def has_add_permission(self, request=None,user=None):
        """
        Return True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_add_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm = get_class_perm('add', self)
        return user.has_perm(perm,self)

    def has_change_permission(self, request=None,user=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_change_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm = get_class_perm('change', self)
        return user.has_perm(perm,self)

    def has_delete_permission(self, request=None,user=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_delete_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm = get_class_perm('delete', self)
        return user.has_perm(perm,self)

    def has_view_permission(self, request=None,user=None):
        """
        Return True if the given request has permission to view the given
        Django model instance. The default implementation doesn't examine the
        `obj` parameter.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_view_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm_view = get_class_perm('view', self)
        perm_change = get_class_perm('change', self)
        return (
            user.has_perm(perm_view,self) or
            user.has_perm(perm_change,self)
        )

    def has_view_or_change_permission(self, request=None,user=None):
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_view_or_change_permission() needs one (and only one) of this arguments: 'request','user'")
        return self.has_view_permission(request=request,user=user) or self.has_change_permission(request=request,user=user)
    
    @classmethod
    def has_global_add_permission(cls, request=None,user=None):
        """
        Return True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_global_add_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm = get_class_perm('add', cls)
        return user.has_perm(perm)
    
    @classmethod
    def has_global_change_permission(cls, request=None,user=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_global_change_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm = get_class_perm('change', cls)
        return user.has_perm(perm,cls)
    
    @classmethod
    def has_global_delete_permission(cls, request=None,user=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_global_delete_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm = get_class_perm('delete', cls)
        return user.has_perm(perm,cls)
    
    @classmethod
    def has_global_view_permission(cls, request=None,user=None):
        """
        Return True if the given request has permission to view the given
        Django model instance. The default implementation doesn't examine the
        `obj` parameter.
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_global_view_permission() needs one (and only one) of this arguments: 'request','user'")
        if request:
            user = request.user.appuser
        perm_view = get_class_perm('view', cls)
        perm_change = get_class_perm('change', cls)
        return (
            user.has_perm(perm_view,cls) or
            user.has_perm(perm_change,cls)
        )
    
    @classmethod
    def has_global_view_or_change_permission(cls, request=None,user=None):
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("has_global_view_or_change_permission() needs one (and only one) of this arguments: 'request','user'")
        return cls.has_global_view_permission(request=request,user=user) or cls.has_global_change_permission(request=request,user=user)
    
    @classmethod
    def filter_for_request(cls,type,request=None,user=None):
        """Use this function to get all the instance for wich a certain user (throughout a request)
        has the permission of specified type

        Args:
            type (str): can have values view,add,change,delete,admin
            request (HttpRequest, optional): the request containing the user. Defaults to None.
            user (User, optional): the user. Defaults to None.

        Returns:
            QuerySet: the queryset containing the instance for wich User has "type" permission. 
        """
        if (request is None and user is None) or (request is not None and user is not None):
            return TypeError("filter_for_request() needs one (and only one) of this arguments: 'request','user'")
        if request is not None:
            user = request.user.appuser
        perm_function = getattr(cls,"has_global_%s_permission"%type)
        if perm_function(request):
            return cls.objects.all()
        
        all_permissions = user.get_all_permissions()
        class_perm = get_class_perm(type,cls)
        ## If i have <app_label>.view_<class_name>.13 this will return 13
        ## If i have <app_label>.view_<class_name> this will raise the value error and the cycle will continue
        all_ids = set()
        for perm in all_permissions:
            try:
                if perm.startswith(class_perm+"."):
                    id_str = perm[perm.index(".",perm.index(".")+1)+1:]
                    id = int(id_str)
                    all_ids.add(int(id_str))
            except ValueError:
                continue
        
        return cls.objects.filter(id__in=all_ids)
    
def auto_create_permissions(sender, instance, created, **kwargs):
    if created:
        instance.create_permissions()
def auto_delete_permissions(sender, instance, **kwargs):
    instance.delete_permissions()

def get_class_permission_codename(type,obj):
    """
    Args:
        type (str): can be "view","change","add","delete"
        obj (models.Model): any model instance

    Returns:
        str: The codename of the corresponding permission
    """
    obj_content_type = ContentType.objects.get_for_model(obj)
    app_label,class_name = obj_content_type.natural_key()
    return '%s_%s'%(type,class_name)

def get_instance_permission_codename(type,obj):
    """
    Args:
        type (str): can be "view","change","add","delete"
        obj (models.Model): any model instance

    Returns:
        str: The codename of the corresponding permission
    """
    obj_content_type = ContentType.objects.get_for_model(obj)
    app_label,class_name = obj_content_type.natural_key()
    return '%s_%s.%s'%(type,class_name,obj.pk)

def get_class_perm(type,obj):
    """
    Args:
        type (str): can be "view","change","add","delete"
        obj (models.Model): any model instance

    Returns:
        str: The codename of the corresponding permission
    """
    obj_content_type = ContentType.objects.get_for_model(obj)
    app_label,class_name = obj_content_type.natural_key()
    return '%s.%s_%s'%(app_label,type,class_name)

def get_instance_perm(type,obj):
    """
    Args:
        type (str): can be "view","change","add","delete"
        obj (models.Model): any model instance

    Returns:
        str: The codename of the corresponding permission
    """
    obj_content_type = ContentType.objects.get_for_model(obj)
    app_label,class_name = obj_content_type.natural_key()
    return '%s.%s_%s.%s'%(app_label,type,class_name,obj.pk)

def get_class_permission_name(type,obj):
    """
    Args:
        type (str): can be "view","change","add","delete"
        obj (models.Model): any model instance

    Returns:
        str: The name of the corresponding permission
    """
    obj_content_type = ContentType.objects.get_for_model(obj)
    app_label,class_name = obj_content_type.natural_key()
    return 'Can %s %s'%(type,class_name)

def get_instance_permission_name(type,obj):
    """
    Args:
        type (str): can be "view","change","add","delete"
        obj (models.Model): any model instance

    Returns:
        str: The name of the corresponding permission
    """
    obj_content_type = ContentType.objects.get_for_model(obj)
    app_label,class_name = obj_content_type.natural_key()
    return 'Can %s %s %s'%(type,class_name,obj.pk)

class AppUser(User):
    """e
    This is the base user of this app. It inherit from User, so all the functionality
    of the User class can be found here.
    """
    from triage.models import Hospital,Totem,Patient
    light_theme = "light"
    darl_theme = "dark"
    THEMES = (
        (light_theme,_("Chiaro")),
        (darl_theme,_("Scuro"))
    )
    theme = models.CharField(verbose_name=_("Tema"),max_length=512, choices=THEMES,default="light")
    img = models.ImageField(verbose_name=_("Immagine del profilo"),null=True,blank=True,upload_to='app/appuser/imgs')
    _dashboard_options = models.TextField(verbose_name=_("Opzioni Dashboard"),default="{}")
    _dashboard_hospital = models.ForeignKey(Hospital,verbose_name=_("Ospedalle attualmente loggato"),on_delete=models.SET_NULL,blank=True,null=True)
    
    ## Other types of users
    totem_logged = models.OneToOneField(Totem,verbose_name=_("Totem"),on_delete=models.CASCADE,blank=True,null=True)
    patient_logged = models.OneToOneField(Patient,verbose_name=_("Paziente"),on_delete=models.CASCADE,blank=True,null=True)
    
    class Meta():
        verbose_name = _("Application User")
        verbose_name_plural = _("Application Users")
            
    @property
    def is_totem(self):
        return self.totem_logged is not None
    @property
    def is_patient(self):
        return self.patient_logged is not None
    @property
    def dashboard_options(self):
        from app.utils import AttributeJson
        return AttributeJson(self,"_dashboard_options")
    @dashboard_options.setter
    def dashboard_options(self,value):
        import json
        self._dashboard_options = json.dumps(value)
    
    @property
    def logged_profile(self):
        return "%s - %s"%(self.username,self.dashboard_hospital)
    
    @property
    def dashboard_hospital(self):
        from triage.models import Hospital
        if self._dashboard_hospital is not None:
            return self._dashboard_hospital
        else:
            hospitals = Hospital.filter_for_request("view",user=self)
            if hospitals.count()==1:
                self._dashboard_hospital = hospitals[0]
                self.save()
                return self._dashboard_hospital
    @dashboard_hospital.setter
    def dashboard_hospital(self,value):
        self._dashboard_hospital = value
    
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
    
    def has_perm(self, class_perm, obj=None):
        if self.is_superuser:
            return True
        has_class_permission = super().has_perm(class_perm)
        if has_class_permission:
            return has_class_permission
        if not obj:
            return has_class_permission

        obj_id = obj.id
        
        instance_perm = class_perm + "." + str(obj_id)
        has_instance_permission = super().has_perm(instance_perm)
        return has_instance_permission
        
@receiver(post_save, sender=User)
def create_appuser(sender, instance, created, **kwargs):
    if created:
        AppUser.extend_parent(instance)

class AppGroup(Group):
    """
    This is the base group of this app. It inherit from Group, so all the functionality
    of the Group class can be found here.
    """
    pass
    class Meta():
        proxy = True
    
    @classmethod
    def get_admins_name(cls,content_type,obj=None):
        if obj:
            return "%s - %s (id: %s) - Admins"%(content_type.name,obj.name,obj.id)
        else:
            return "%s - Admins"%(content_type.name)
    @classmethod
    def get_creators_name(cls,content_type,obj=None):
        if obj:
            return "%s - %s (id: %s) - Creators"%(content_type.name,obj.name,obj.id)
        else:
            return "%s - Creators"%(content_type.name)
    @classmethod
    def get_editors_name(cls,content_type,obj=None):
        if obj:
            return "%s - %s (id: %s) - Editors"%(content_type.name,obj.name,obj.id)
        else:
            return "%s - Editors"%(content_type.name)
    @classmethod
    def get_viewers_name(cls,content_type,obj=None):
        if obj:
            return "%s - %s (id: %s) - Viewers"%(content_type.name,obj.name,obj.id)
        else:
            return "%s - Viewers"%(content_type.name)  

