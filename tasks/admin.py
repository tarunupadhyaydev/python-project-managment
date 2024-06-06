from django.contrib import admin
from .models import Task
from django.forms import TextInput, Textarea,Select
from django.db import models
from django.utils.html import format_html

# Register your models here.
# admin.site.register(Task)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
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


    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(TaskAdmin, self).get_form(request, obj, **kwargs)
    #     field = form.base_fields["project"]
    #     field.widget.can_add_related = False
    #     field.widget.can_change_related = False
    #     field.widget.can_delete_related = False
    #     return form

    list_display = ("name", "project", "task_due_date",)


    @admin.display(description="Due Date")
    def task_due_date(self, obj):
         return obj.due_date  and format_html(
            '<span class="btn btn-link-dark btn-sm" style="background-color:#ddd"><i class="fas fa-clock" aria-hidden="true"></i> {}</span>',
            obj.due_date.strftime('%d %b %Y'),
        )

    fieldsets = (
        (None, {'fields': ('project','due_date','name','description','status','priority',)}),
        # ('Project Administrator Info', {'fields': ('administrator_name', 'administrator_email',)}),
        # ('Project Other Details', {'fields': ('reception_telephone', 'start_date','duration','value','project_address',)}),
        # ('Project Cost Center Details', {'fields': ('cost_center', 'cost_center_number','cost_center_description',)}),
        # #(None, {'fields': ('created_by',)})
        # ('Permissions', {'fields': ('is_superuser','groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('project','due_date','name','description','status','priority',)},
            # ('Project Administrator Info', {'fields': ('administrator_name', 'administrator_email',)}),
            # ('Project Other Details', {'fields': ('reception_telephone', 'start_date','duration','value','project_address',)}),
            # ('Project Cost Center Details', {'fields': ('cost_center', 'cost_center_number','cost_center_description',)}),
            # # 'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    #search_fields = ('name',)
    ordering = ('-created_at',)
