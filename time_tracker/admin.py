from django.contrib import admin
from .models import TimeTracker
from django.forms import TextInput, Textarea,Select,TimeInput
from django.db import models
from django.utils.html import format_html
from datetime import datetime, timedelta
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
# Register your models here.


def calculate_duration(date,start_time, end_time):
    start = datetime.combine(date, start_time)
    end = datetime.combine(date, end_time)
    if end < start:
        end += timedelta(days=1)  # Handle end time being after midnight
    duration = end - start
    return duration

@admin.register(TimeTracker)
class MemberAdmin(admin.ModelAdmin):
  formfield_overrides = {
       # models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.CharField: {'widget': TextInput(attrs={'style':'width:25em'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40,'style':'width:25em'})},
        models.ForeignKey: {'widget': Select(attrs={'style':'width:25em;margin-top:5px'})},
         models.TimeField: {'widget': Select(attrs={'style':'width:25em;margin-top:5px'})},
        models.TimeField:{'widget': TimeInput(attrs={'type': 'time'})}
    }

  def formfield_for_dbfield(self, *args, **kwargs):
        formfield = super().formfield_for_dbfield(*args, **kwargs)

        formfield.widget.can_delete_related = False
        formfield.widget.can_change_related = False
        formfield.widget.can_add_related = False
        formfield.widget.can_view_related = False

        return formfield

  list_display = ("project_task_info","date","timeline_start_time","timeline_end_time","timeline_duration","timeline_status",)

  fieldsets = (
        (None, {'fields': ('date','start_time','end_time','project','task',)}),
        # #(None, {'fields': ('created_by',)})
    )
  add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('date','start_time','end_time','project','task',)},
        ),
    )

  def get_fieldsets(self, request, obj=None):
    # If the object is being added (obj is None), use add_fieldsets
    if not obj:
        fieldsets = self.add_fieldsets
    else:
        fieldsets = super().get_fieldsets(request, obj)
    
    # Add the 'groups' field for superusers when adding an object
    if obj and request.user.is_superuser:
        fieldsets = list(fieldsets)  # Convert to list to allow modifications
        fieldsets.append(('Approve/Reject', {'fields': ('status',)}))
    elif obj and request.user.groups.filter(name='superadmin').exists():
        fieldsets = list(fieldsets)
        fieldsets.append(('Approve/Reject', {'fields': ('status',)}))
    
    return fieldsets

  @admin.display(description="Project/Task")
  def project_task_info(self, obj):
      return (obj.project or obj.task) and format_html(
        '<p style="margin:0px;padding:0px;color:#000;font-size:16px;font-weight:600">{}</p><p style="margin:0px;padding:0px;font-size:14px">#{}</p>',
        obj.project,
        obj.task,
    )

  @admin.display(description="Status")
  def timeline_status(self, obj):
        status = obj.status
        
        if status == 'RJ':
          project_status = 'Rejected'
          status_class = 'btn-danger'
        elif status == 'AP':
          project_status = 'Approved'
          status_class = 'btn-success'
        else :
          project_status = 'Pending'
          status_class = 'btn-warning'
        return obj.status  and format_html(
          '<span class="btn {} btn-sm" style="border-radius: 40px;">{}</span>',
          status_class,
          project_status,
      )

  @admin.display(description="Start Time")
  def timeline_start_time(self, obj):
         return obj.start_time  and format_html(
            '<span >{}</span>',
            obj.start_time,
        )

  @admin.display(description="End Time")
  def timeline_end_time(self, obj):
         return obj.end_time  and format_html(
            '<span >{}</span>',
            obj.end_time,
        )

  @admin.display(description="Duration")
  def timeline_duration(self, obj):
         return obj.duration  and format_html(
            '<span class="btn btn-link-dark btn-sm" style="background-color:#ddd"><i class="fas fa-clock" aria-hidden="true"></i> {}</span>',
            obj.duration,
        )

  def get_list_display_links(self, request, list_display):
        if request.user.groups.filter(name='superadmin').exists():
          logging.info(list_display)
          return ('project_task_info',)
        return None

  def save_model(self, request, obj, form, change):
    if not obj.pk:
        obj.created_by = request.user
        obj.duration = calculate_duration(obj.date,obj.start_time,obj.end_time)
    super().save_model(request, obj, form, change)
  #search_fields = ('description',)
  ordering = ('-created_at',)
