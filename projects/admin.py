from django.contrib import admin
from .models import Project
from django.utils.html import format_html
from django.forms import TextInput, Textarea
from django.db import models

# Register your models here.

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style':'width:20em'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':40})},
    }
    list_display = ("project_info","administrator_info","reception_telephone","project_status", "start_date", "project_duration","project_value")

    fieldsets = (
        (None, {'fields': ('name','project_number','status',)}),
        ('Project Administrator Info', {'fields': ('administrator_name', 'administrator_email',)}),
        ('Project Other Details', {'fields': ('reception_telephone', 'start_date','duration','value','project_address',)}),
        ('Project Cost Center Details', {'fields': ('cost_center', 'cost_center_number','cost_center_description',)}),
        #(None, {'fields': ('created_by',)})
        # ('Permissions', {'fields': ('is_superuser','groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name','project_number','status',)},
            ('Project Administrator Info', {'fields': ('administrator_name', 'administrator_email',)}),
            ('Project Other Details', {'fields': ('reception_telephone', 'start_date','duration','value','project_address',)}),
            ('Project Cost Center Details', {'fields': ('cost_center', 'cost_center_number','cost_center_description',)}),
            # 'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    @admin.display(description="Project Name")
    def project_info(self, obj):
         return (obj.name or obj.project_number) and format_html(
            '<p style="margin:0px;padding:0px;color:#000;font-size:16px;font-weight:600">{}</p><p style="margin:0px;padding:0px;font-size:14px">#{}</p>',
            obj.name,
            obj.project_number,
        )

    @admin.display(description="Administrator")
    def administrator_info(self, obj):
         return (obj.administrator_name or obj.administrator_email) and format_html(
            '<p style="margin:0px;padding:0px;color:#000;font-size:16px;font-weight:600">{}</p><p style="margin:0px;padding:0px;font-size:14px">{}</p>',
            obj.administrator_name,
            obj.administrator_email,
        )

    @admin.display(description="Start Date")
    def project_start_date(self, obj):
         return obj.start_date  and format_html(
            '<p style="margin:0px;padding:0px;">{}</p>',
            obj.start_date,
        )

    @admin.display(description="Duration")
    def project_duration(self, obj):
         return obj.duration  and format_html(
            '<span class="btn btn-link-dark btn-sm" style="background-color:#ddd"><i class="fas fa-clock" aria-hidden="true"></i> {}</span>',
            obj.duration,
        )

    @admin.display(description="Status")
    def project_status(self, obj):
         status = obj.status
         
         if status == 'IP':
            project_status = 'In-Progress'
            status_class = 'btn-outline-info'
         elif status == 'CP':
            project_status = 'Completed'
            status_class = 'btn-outline-success'
         else :
            project_status = 'Open'
            status_class = 'btn-outline-warning'
         return obj.status  and format_html(
            '<span class="btn {} btn-sm" style="border-radius: 40px;">{}</span>',
            status_class,
            project_status,
        )

    @admin.display(description="Value")
    def project_value(self, obj):
         return obj.value  and format_html(
            '<p style="margin:0px;padding:0px;">{}</p>',
            obj.value,
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

   # search_fields = ('name',)
    ordering = ('-created_at',)