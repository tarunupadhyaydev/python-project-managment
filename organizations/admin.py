from django.contrib import admin,messages
from .models import Organization
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ngettext
from django.utils.translation import gettext_lazy as _

# Register your models here.
# admin.site.register(Organization)

@admin.register(Organization)
class MemberAdmin(admin.ModelAdmin):
  list_display = ("name", "created_at", "updated_at","status",)
  actions = ["restore_selected","soft_delete_selected", "hard_delete_selected"]
  fieldsets = (
      (None, {'fields': ('name',)}),
  )

  @admin.display(description="Status")
  def status(self, obj):
        return obj.deleted_at and format_html(
          '<span class="badge badge-danger">Inactive</span>',
          obj.deleted_at,
      ) or format_html(
          '<span class="badge badge-success">Active</span>',
          obj.deleted_at,
      )

  def get_actions(self, request):
      actions = super().get_actions(request)
      if request.user.is_superuser:
          return actions
      else :
          if "hard_delete_selected" in actions:
              del actions["hard_delete_selected"]
          return actions
  # ......organizations actions starts .........#
  @admin.action(description=_('Active selected organizations'))
  def restore_selected(self, request, queryset):
      updated = queryset.update(deleted_at=None)
      self.message_user(
          request,
          ngettext(
              "%d organization has been active.",
              "%d organizations have been active.",
              updated,
          )
          % updated,
          messages.SUCCESS,
      )

  @admin.action(description=_('Inactive selected organizations'))
  def soft_delete_selected(self, request, queryset):
      updated = queryset.update(deleted_at=timezone.now())
      self.message_user(
          request,
          ngettext(
              "%d organization has been inactive.",
              "%d organizations have been inactive..",
              updated,
          )
          % updated,
          messages.ERROR,
      )

  @admin.action(description=_('Permanently delete selected organizations'))
  def hard_delete_selected(self, request, queryset):
      deleted = queryset.delete()
      self.message_user(
          request,
          "selected organizations have been permanently deleted.",
          messages.ERROR,
      )

  #..... organizations actions end .............#

  def get_queryset(self, request):
    #logging.info(request.user.groups.all())
    #logging.info(request.user.organization)
    qs = super().get_queryset(request)
    if request.user.is_superuser:
      return qs
    else :
      return qs.filter(created_by=request.user) 

  
  def has_delete_permission(self, request, obj=None):
    # Remove the default delete action
    return False


  def save_model(self, request, obj, form, change):
    if not obj.pk:
        obj.created_by = request.user
    super().save_model(request, obj, form, change)


 # search_fields = ('name',)
  #ordering = ('name',)
  ordering = ('-created_at',)