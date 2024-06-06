# users/admin.py
from django.contrib import admin,messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User
from django.utils import timezone
from django.utils.translation import ngettext
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from organizations.models import Organization
from django.forms import TextInput, Textarea,Select
from django.db import models
import logging, logging.config
import sys

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

logging.config.dictConfig(LOGGING)

class CustomUserAdmin(UserAdmin):
    formfield_overrides = {
       # models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.CharField: {'widget': TextInput(attrs={'style':'width:25em'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40,'style':'width:25em'})},
        models.ForeignKey: {'widget': Select(attrs={'style':'width:25em;margin-top:5px'})},
    }

    def formfield_for_dbfield(self, *args, **kwargs):
        formfield = super().formfield_for_dbfield(*args, **kwargs)

        formfield.widget.can_delete_related = False
        formfield.widget.can_change_related = False
        formfield.widget.can_add_related = False
        formfield.widget.can_view_related = False

        return formfield

    model = User
    list_display = ('info','organization','contact_number','designation','get_groups','is_active','deleted_status',)
    list_display_links = ("info",) # Here
    #list_filter = ('organization',)
    list_filter = []  # Disable filters
    actions = ["active_selected","deactive_selected","soft_delete_selected", "restore_selected","hard_delete_selected"]
    #property
    def get_list_display(self,request):
        if request.user.is_superuser:
            return ('info','organization','contact_number','designation','get_groups','is_active','deleted_status')
        return ('info','organization','contact_number','designation','is_active','deleted_status')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser:
            return actions
        else :
            if "hard_delete_selected" in actions:
                del actions["hard_delete_selected"]
            return actions

    @admin.display(description="Info")
    def info(self, obj):
         return (obj.full_name or obj.email) and format_html(
            '<p style="margin:0px;padding:0px;color:#000;font-weight:500">{}</p><p style="margin:0px;padding:0px;">{}</p>',
            obj.full_name,
            obj.email,
        )

    @admin.display(description="")
    def deleted_status(self, obj):
            return obj.deleted_at and format_html(
            '<span class="badge badge-danger">Deleted</span>',
            obj.deleted_at,
        ) or format_html(
          '<span ></span>',
          obj.deleted_at,
      ) 
    # ......user actions starts .........#
    @admin.action(description=_('Restore selected users'))
    def restore_selected(self, request, queryset):
        updated = queryset.update(is_active=True,deleted_at=None)
        self.message_user(
            request,
            ngettext(
                "%d user has been restored.",
                "%d users have been restored.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description=_('Delete selected users'))
    def soft_delete_selected(self, request, queryset):
        updated = queryset.update(is_active=False,deleted_at=timezone.now())
        self.message_user(
            request,
            ngettext(
                "%d user has been deleted.",
                "%d users have been deleted..",
                updated,
            )
            % updated,
            messages.ERROR,
        )

    @admin.action(description=_('Permanently delete selected users'))
    def hard_delete_selected(self, request, queryset):
        deleted = queryset.delete()
        self.message_user(
            request,
            "selected users have been permanently deleted.",
            messages.ERROR,
        )

    @admin.action(description=_('Set active selected users'))
    def active_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            ngettext(
                "%d user has been set active.",
                "%d users have been set active",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description=_('Set deactive selected users'))
    def deactive_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            ngettext(
                "%d user has been deactive.",
                "%d users have been deactive..",
                updated,
            )
            % updated,
            messages.ERROR,
        )

    #..... user actions end .............#

    def get_groups(self, obj):
        return ','.join([g.name for g in obj.groups.all()]) if obj.groups.count() else ''
    get_groups.short_description = 'Group'

    @admin.display(description="Contact Number")
    def contact_number(self, obj):
         return (obj.telephone or obj.mobile) and format_html(
            '<p style="margin:0px;padding:0px;">Telephone:{}</p><p style="margin:0px;padding:0px;">Cell Phone:{}</p>',
            obj.telephone,
            obj.mobile,
        )
        
    fieldsets = (
        (None, {'fields': ('username','email', 'password','is_active',)}),
        # ('Personal Info', {'fields': ('first_name', 'last_name','organization','designation','job_type')}),
        # ('Contact Details', {'fields': ('telephone', 'mobile','address','postal_address')}),
        #(None, {'fields': ('created_by',)})
        # ('Permissions', {'fields': ('is_superuser','groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'password1', 'password2')}
            # 'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    def get_fieldsets(self, request, obj=None):
        # If the object is being added (obj is None), use add_fieldsets
        if not obj:
            fieldsets = self.add_fieldsets
        else:
            fieldsets = super().get_fieldsets(request, obj)
        
        # Add the 'groups' field for superusers when adding an object
        if not obj and request.user.is_superuser:
            fieldsets = list(fieldsets)  # Convert to list to allow modifications
            fieldsets.append(('Permissions', {'fields': ('groups',)}))
        elif obj and request.user.is_superuser and obj.groups.filter(name='superadmin').exists():
            fieldsets = list(fieldsets)
            fieldsets.append(('Personal Info', {'fields': ('first_name', 'last_name','designation','job_type')}))
            fieldsets.append(('Contact Details', {'fields': ('telephone', 'mobile','address','postal_address')}))
            fieldsets.append(('Permissions', {'fields': ('groups',)}))
        elif obj and request.user.is_superuser:
            fieldsets = list(fieldsets)
            fieldsets.append(('Personal Info', {'fields': ('first_name', 'last_name','organization','designation','job_type')}))
            fieldsets.append(('Contact Details', {'fields': ('telephone', 'mobile','address','postal_address')}))
            fieldsets.append(('Permissions', {'fields': ('groups',)}))
        elif obj and request.user.groups.filter(name='superadmin').exists():
            fieldsets = list(fieldsets)
            fieldsets.append(('Personal Info', {'fields': ('first_name', 'last_name','organization','designation','job_type')}))
            fieldsets.append(('Contact Details', {'fields': ('telephone', 'mobile','address','postal_address')}))
        elif obj :
            fieldsets = list(fieldsets)
            fieldsets.append(('Personal Info', {'fields': ('first_name', 'last_name','designation','job_type')}))
            fieldsets.append(('Contact Details', {'fields': ('telephone', 'mobile','address','postal_address')}))
        
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is None when creating a new user
            return []
        return []

    def get_queryset(self, request):
        #logging.info(request.user.groups.all())
        #logging.info(request.user.organization)
        qs = super().get_queryset(request)
        if request.user.is_superuser:
          return qs
        elif request.user.groups.filter(name='superadmin').exists() :
          return qs.filter(groups__name='employee',created_by=request.user)
        elif request.user.groups.filter(name='admin').exists() :
          #employee_group = Group.objects.get(name="employee")
          #logging.info(request.user.groups.filter(name='admin'))
          return qs.filter(groups__name='employee',created_by=request.user)
        else :
          return qs.filter(created_by=request.user) 

    def has_delete_permission(self, request, obj=None):
      # Remove the default delete action
      return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.is_superuser :
            kwargs["queryset"] = Organization.objects.filter(deleted_at__isnull=True)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        elif db_field.name == "organization":
            kwargs["queryset"] = Organization.objects.filter(created_by=request.user,deleted_at__isnull=True)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.organization = request.user.organization
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
       
               # Ensure the user is saved before adding them to the group
        if not change:
            # Get or create the 'employee' group
            employee_group = Group.objects.get(name='employee')
            # Add the created_by user to the 'employee' group
            obj.groups.add(employee_group)

    #search_fields = ('email',)
    search_fields = []
    #readonly_fields = ('username',)
    ordering = ('-created_at',)

admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)